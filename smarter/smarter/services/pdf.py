'''
Created on May 17, 2013

@author: dip
'''
from services.tasks.pdf import prepare, pdf_merge, get, archive, hpz_upload_cleanup, \
    group_separator, bulk_pdf_cover_sheet
from urllib.parse import urljoin
from pyramid.view import view_config
from pyramid.response import Response
from smarter.security.context import check_context
from edapi.exceptions import InvalidParameterError, ForbiddenError
from edauth.security.utils import get_session_cookie
import urllib.parse
from sqlalchemy.sql import and_, select
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.security.context import select_with_context
from smarter.reports.helpers.filters import apply_filter_to_query
from edapi.httpexceptions import EdApiHTTPPreconditionFailed, \
    EdApiHTTPForbiddenAccess, EdApiHTTPInternalServerError, EdApiHTTPNotFound
from services.exceptions import PdfGenerationError
from smarter.reports.helpers.ISR_pdf_name_formatter import generate_isr_report_path_by_student_id
from smarter.reports.helpers.constants import AssessmentType, Constants
from smarter.reports.helpers.filters import FILTERS_CONFIG
import services.celery
from edapi.decorators import validate_params
from edcore.utils.utils import to_bool, merge_dict
from hpz_client.frs.file_registration import register_file
from celery.canvas import group, chain
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request
import copy
from datetime import datetime
import json
import os
from smarter_common.security.constants import RolesConstants
import pyramid
from batch.pdf.pdf_generator import PDFGenerator
from services.constants import ServicesConstants
from smarter.reports.helpers.metadata import get_custom_metadata
import logging

logger = logging.getLogger(__name__)

KNOWN_REPORTS = ['indivStudentReport.html']

PDF_PARAMS = {
    "type": "object",
    "additionalProperties": False,
    "properties": merge_dict({
        Constants.STATECODE: {
            "type": "string",
            "required": True,
            "pattern": "^[a-zA-Z]{2}$"
        },
        Constants.STUDENTGUID: {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9\-]{0,50}$"
            },
            "minItems": 1,
            "uniqueItems": True,
            "required": False
        },
        Constants.DISTRICTGUID: {
            "type": "string",
            "required": False,
            "pattern": "^[a-zA-Z0-9\-]{0,50}$",
        },
        Constants.SCHOOLGUID: {
            "type": "string",
            "required": False,
            "pattern": "^[a-zA-Z0-9\-]{0,50}$",
        },
        Constants.ASMTGRADE: {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[0-9]{1,2}$"
            },
            "minitems": 1,
            "uniqueItems": True,
            "required": False
        },
        Constants.ASMTTYPE: {
            "type": "string",
            "required": False,
            "pattern": "^(" + AssessmentType.INTERIM_ASSESSMENT_BLOCKS + "|" + AssessmentType.SUMMATIVE + "|" + AssessmentType.INTERIM_COMPREHENSIVE + ")$",
        },
        Constants.ASMTYEAR: {
            "type": "integer",
            "required": True,
            "pattern": "^2[0-9]{3}$"
        },
        Constants.DATETAKEN: {
            "type": "integer",
            "required": False,
            "pattern": "^[0-9]{8}$"
        },
        Constants.MODE: {
            "type": "string",
            "required": False,
            "pattern": "^(gray|GRAY|color|COLOR)$",
        },
        Constants.LANG: {
            "type": "string",
            "required": False,
            "pattern": "^[a-z]{2}$",
        },
        Constants.PDF: {
            "type": "string",
            "required": False,
            "pattern": "^(true|false|TRUE|FALSE)$",
        },
        Constants.SL: {
            "type": "string",
            "required": False,
            "pattern": "^\d+$",
        }
    }, FILTERS_CONFIG)
}


@view_config(route_name='pdf', request_method='POST')
@validate_params(schema=PDF_PARAMS)
def async_pdf_service(context, request):
    '''
    This is for backward compitibility and batch PDFs.
    '''
    logger.info('PDF request made')
    return send_pdf_request(request.validated_params)


@view_config(route_name='pdf', request_method='GET')
@validate_params(schema=PDF_PARAMS)
def sync_pdf_service(context, request):
    '''
    Handles POST request to /services/pdf

    :param request:  Pyramid request object
    '''
    logger.info('PDF request made')
    return send_pdf_request(request.validated_params, sync=True)


def send_pdf_request(params, sync=False):
    '''
    Requests for pdf content, throws http exceptions when error occurs

    :param params: python dict that contains query parameters from the request
    '''
    try:
        response = get_pdf_content(params, sync)
    except InvalidParameterError as e:
        logger.error('PDF generation : invaid parameter')
        raise EdApiHTTPPreconditionFailed(e.msg)
    except ForbiddenError as e:
        logger.error('PDF generation : access forbidden')
        raise EdApiHTTPForbiddenAccess(e.msg)
    except (PdfGenerationError, TimeoutError) as e:
        logger.error('PDF generation for Extraction failed')
        raise EdApiHTTPInternalServerError(e.msg)
    except Exception as e:
        # if celery get task got timed out...
        logger.error('PDF generation : celery timeout')
        raise EdApiHTTPInternalServerError("Internal Error")

    return response


def get_pdf_content(params, sync=False):
    # Collect the parameters
    student_ids = params.get(Constants.STUDENTGUID)
    state_code = params.get(Constants.STATECODE)
    district_id = params.get(Constants.DISTRICTGUID)
    school_id = params.get(Constants.SCHOOLGUID)
    grades = params.get(Constants.ASMTGRADE, [])
    asmt_type = params.get(Constants.ASMTTYPE, AssessmentType.SUMMATIVE)
    asmt_year = params.get(Constants.ASMTYEAR)
    date_taken = str(params.get(Constants.DATETAKEN)) if params.get(Constants.DATETAKEN) is not None else None
    color_mode = params.get(Constants.MODE, Constants.GRAY).lower()
    lang = params.get(Constants.LANG, 'en').lower()
    subprocess_timeout = services.celery.TIMEOUT
    is_grayscale = (color_mode == Constants.GRAY)

    # Validate report type
    report = pyramid.threadlocal.get_current_request().matchdict[Constants.REPORT]
    if report not in KNOWN_REPORTS:
        logger.error('PDF generation : unknown report')
        raise EdApiHTTPNotFound("Not Found")

    # Check that we have either a list of student GUIDs or a district/school/grade combination in the params
    if student_ids is None and (district_id is None or school_id is None or grades is None):
        logger.error('PDF generation : Required parameter is missing')
        raise InvalidParameterError('Required parameter is missing')

    # Validate necessary assessment information
    if (asmt_type == AssessmentType.SUMMATIVE or asmt_type == AssessmentType.INTERIM_COMPREHENSIVE) and asmt_year is None and date_taken is None:
        logger.error('PDF generation : Required parameters asmt_year and date_taken is missing')
        raise InvalidParameterError('Required parameter is missing')

    settings = pyramid.threadlocal.get_current_registry().settings
    celery_timeout = int(settings.get('pdf.celery_timeout', '30'))
    always_generate = to_bool(settings.get('pdf.always_generate', False))

    # Set up a couple additional variables
    base_url = urljoin(pyramid.threadlocal.get_current_request().application_url, '/assets/html/' + report)
    pdf_base_dir = settings.get('pdf.report_base_dir', "/tmp")

    if sync:
        # Get cookies and other config items
        (cookie_name, cookie_value) = get_session_cookie()
        single_generate_queue = settings.get('pdf.single_generate.queue')
        response = get_single_pdf_content(pdf_base_dir, base_url, cookie_value, cookie_name, subprocess_timeout, state_code, asmt_year, date_taken, asmt_type, student_ids, lang, is_grayscale, always_generate, celery_timeout, params, single_generate_queue)
    else:
        response = get_bulk_pdf_content(settings, pdf_base_dir, base_url, subprocess_timeout, student_ids, grades, state_code, district_id, school_id, asmt_type, asmt_year, lang, is_grayscale, always_generate, celery_timeout, params)
    return response


def get_single_pdf_content(pdf_base_dir, base_url, cookie_value, cookie_name, subprocess_timeout, state_code, asmt_year,
                           date_taken, asmt_type, student_id, lang, is_grayscale, always_generate, celery_timeout,
                           params, single_generate_queue):
    logger.info('Getting single PDF content')
    if type(student_id) is list:
        student_id = student_id[0]

    # Get all file names
    if not _has_context_for_pdf_request(state_code, student_id):
        raise ForbiddenError('Access Denied')
    url = _create_student_pdf_url(student_id, base_url, params, date_taken)
    files_by_guid = generate_isr_report_path_by_student_id(state_code, date_taken, asmt_year,
                                                           pdf_report_base_dir=pdf_base_dir, student_ids=[student_id],
                                                           asmt_type=asmt_type, grayScale=is_grayscale, lang=lang)
    file_name = files_by_guid[student_id][date_taken]
    args = (cookie_value, url, file_name)
    options = {'cookie_name': cookie_name, 'timeout': subprocess_timeout, 'grayscale': is_grayscale, 'always_generate': always_generate}

    celery_response = get.apply_async(args=args, kwargs=options, queue=single_generate_queue)  # @UndefinedVariable
    pdf_stream = celery_response.get(timeout=celery_timeout)

    return Response(body=pdf_stream, content_type=Constants.APPLICATION_PDF)


def get_bulk_pdf_content(settings, pdf_base_dir, base_url, subprocess_timeout, student_ids, grades,
                         state_code, district_id, school_id, asmt_type, asmt_year, lang,
                         is_grayscale, always_generate, celery_timeout, params):
    '''
    Read pdf content from file system if it exists, else generate it

    :param params: python dict that contains query parameters from the request
    '''
    logger.info('Getting bulk PDF content')
    # Get the user
    user = authenticated_userid(get_current_request())

    # If we do not have a list of student GUIDs, we need to get it
    all_guids, guids_by_grade = _create_student_ids(student_ids, grades, state_code, district_id, school_id,
                                                    asmt_type, asmt_year, params)

    # Get all file names
    date_taken = None
    files_by_student_id = generate_isr_report_path_by_student_id(state_code, date_taken, asmt_year,
                                                                 pdf_report_base_dir=pdf_base_dir,
                                                                 student_ids=all_guids, asmt_type=asmt_type,
                                                                 grayScale=is_grayscale, lang=lang)

    # Set up a few additional variables
    urls_by_student_id = _create_urls_by_student_id(all_guids, state_code, base_url, params, files_by_student_id)

    # Register expected file with HPZ
    registration_id, download_url, web_download_url = register_file(user.get_uid(), user.get_email())

    # Get the name of the school
    school_name = _get_school_name(state_code, district_id, school_id)

    # Set up directory and file names
    directory_to_archive = os.path.join(pdf_base_dir, Constants.BULK, registration_id, Constants.DATA)
    directory_for_merged_pdfs = os.path.join(pdf_base_dir, Constants.BULK, registration_id, Constants.MERGED)
    directory_for_cover_sheets = os.path.join(pdf_base_dir, Constants.BULK, registration_id, Constants.COVER)
    directory_for_zip = os.path.join(pdf_base_dir, Constants.BULK, registration_id, Constants.ZIP)
    archive_file_name = _get_archive_name(school_name, lang, is_grayscale)
    archive_file_path = os.path.join(directory_for_zip, archive_file_name)

    # Create JSON response
    response = {Constants.FILES: [{Constants.FILENAME: archive_file_name, Constants.DOWNLOAD_URL: download_url, Constants.WEB_DOWNLOAD_URL: web_download_url}]}

    # Generate cookie
    pdfGenerator = PDFGenerator(settings)

    # Create the tasks for each individual student PDF file we want to merge
    generate_tasks = _create_pdf_generate_tasks(pdfGenerator.cookie_value, pdfGenerator.cookie_name, is_grayscale, always_generate, files_by_student_id,
                                                urls_by_student_id)

    # Create the tasks to merge each PDF by grade
    merge_tasks, merged_pdfs_by_grade, student_report_count_by_pdf = _create_pdf_merge_tasks(pdf_base_dir,
                                                                                      directory_for_merged_pdfs,
                                                                                      guids_by_grade,
                                                                                      files_by_student_id,
                                                                                      school_name, lang, is_grayscale)

    # Get metadata for tenant branding
    custom_metadata = get_custom_metadata(state_code)

    # Create tasks for cover sheets
    cover_sheet_tasks, cover_sheets_by_grade = _create_cover_sheet_generate_tasks(pdfGenerator.cookie_value,
                                                                                  pdfGenerator.cookie_name,
                                                                                  is_grayscale, school_name,
                                                                                  user._User__info['name']['fullName'],
                                                                                  custom_metadata,
                                                                                  directory_for_cover_sheets,
                                                                                  merged_pdfs_by_grade,
                                                                                  student_report_count_by_pdf)

    # Create tasks to merge in cover sheets
    merge_covers_tasks = _create_pdf_cover_merge_tasks(merged_pdfs_by_grade, cover_sheets_by_grade,
                                                       directory_to_archive, pdf_base_dir)

    # Start the bulk merge
    _start_bulk(archive_file_path, directory_to_archive, registration_id, generate_tasks, merge_tasks,
                cover_sheet_tasks, merge_covers_tasks, pdf_base_dir)

    # Return the JSON response while the bulk merge runs asynchronously
    return Response(body=json.dumps(response), content_type=Constants.APPLICATION_JSON)


def _create_student_ids(student_ids, grades, state_code, district_id, school_id, asmt_type, asmt_year, params):
    '''
    create list of student guids by grades
    '''
    # If we do not have a list of student GUIDs, we need to get it
    all_guids = []
    guids_by_grade = {}
    if student_ids is None:
        for grade in grades:
            guids = _get_student_ids(state_code, district_id, school_id, asmt_type, params, asmt_year=asmt_year, grade=grade)
            if len(guids) > 0:
                guids_by_grade[grade] = []
                for result in guids:
                    all_guids.append(result[Constants.STUDENT_ID])
                    guids_by_grade[grade].append(result[Constants.STUDENT_ID])
    else:
        grade = None
        if grades is not None and len(grades) == 1:
            grade = grades[0]
        guids = _get_student_ids(state_code, district_id, school_id, asmt_type, params, asmt_year=asmt_year,
                                 grade=grade, student_ids=student_ids)
        grade = 'all' if grade is None else grade
        if len(guids) > 0:
            guids_by_grade[grade] = []
            for result in guids:
                all_guids.append(result[Constants.STUDENT_ID])
                guids_by_grade[grade].append(result[Constants.STUDENT_ID])
    if len(all_guids) == 0:
        raise InvalidParameterError('No students match filters')
    return all_guids, guids_by_grade


def _create_urls_by_student_id(all_guids, state_code, base_url, params, files_by_student_id):
    '''
    create ISR URL link for each students
    '''
    if type(all_guids) is not list:
        all_guids = [all_guids]
    # Set up a few additional variables
    urls_by_guid = {}

    # Check if the user has access to PII for all of these students
    if not _has_context_for_pdf_request(state_code, all_guids):
        raise ForbiddenError('Access Denied')

    for student_id, date_path in files_by_student_id.items():
        for date_taken in date_path:
            url_by_date = {}
            url_by_date[date_taken] = _create_student_pdf_url(student_id, base_url, params, date_taken)
            if student_id in urls_by_guid:
                url_by_date.update(urls_by_guid[student_id])
            urls_by_guid[student_id] = url_by_date
    return urls_by_guid


def _create_pdf_generate_tasks(cookie_value, cookie_name, is_grayscale, always_generate, files_by_guid, urls_by_guid):
    '''
    create celery tasks to prepare pdf files.
    '''
    generate_tasks = []
    args = {Constants.COOKIE: cookie_value, Constants.TIMEOUT: services.celery.TIMEOUT, Constants.COOKIE_NAME: cookie_name,
            Constants.GRAYSCALE: is_grayscale, Constants.ALWAYS_GENERATE: always_generate}

    for student_id, file_name_by_date in files_by_guid.items():
        for date_taken, file_name in file_name_by_date.items():
            copied_args = copy.deepcopy(args)
            copied_args[Constants.URL] = urls_by_guid[student_id][date_taken]
            copied_args[Constants.OUTPUTFILE] = file_name
            generate_tasks.append(prepare.subtask(kwargs=copied_args, immutable=True))  # @UndefinedVariable
    return generate_tasks


def _create_pdf_merge_tasks(pdf_base_dir, directory_for_merged, guids_by_grade, files_by_guid,
                            school_name, lang, is_grayscale):
    '''
    create pdf merge tasks
    '''
    merge_tasks = []
    bulk_paths = {}
    counts_by_grade = {}
    if guids_by_grade:
        for grade, student_ids in guids_by_grade.items():
            if type(student_ids) is not list:
                student_ids = [student_ids]
            # Create bulk output name and path
            bulk_name = _get_merged_pdf_name(school_name, grade, lang, is_grayscale)
            bulk_path = os.path.join(directory_for_merged, bulk_name)

            # Get the files for this grade
            file_names = []
            for student_id in student_ids:
                filenames = files_by_guid[student_id].values()
                for file_name in filenames:
                    file_names.append(file_name)

            # Create the merge task
            merge_tasks.append(pdf_merge.subtask(args=(file_names, bulk_path, pdf_base_dir), immutable=True))  # @UndefinedVariable
            bulk_paths[grade] = bulk_path
            counts_by_grade[grade] = len(file_names)
    return merge_tasks, bulk_paths, counts_by_grade


def _create_cover_sheet_generate_tasks(cookie_value, cookie_name, is_grayscale, school_name, user_name, custom_metadata,
                                       directory_for_covers, merged_by_grade, student_report_count_by_grade):
    cover_tasks = []
    cover_sheets_by_grade = {}
    cv_base_url = urljoin(pyramid.threadlocal.get_current_request().application_url, '/assets/html/pdfCoverPage.html')
    cv_params = {
        'schoolName': school_name,
        'user': user_name,
        'date': str(datetime.now().strftime("%m/%d/%Y")),
        'pageCount': '',
        'studentCount': '',
        'grade': ''
    }
    if is_grayscale:
        cv_params['gray'] = True
    branding = custom_metadata.get(Constants.BRANDING)
    if branding:
        cv_params['tenant_logo'] = branding.get('image')
        cv_params['tenant_label'] = branding.get('display')
    if merged_by_grade:
        for grade, merged_path in merged_by_grade.items():
            # Create cover sheet output name and path
            cover_name = _get_cover_sheet_name(grade)
            cover_path = os.path.join(directory_for_covers, cover_name)

            # Update the parameters for the URL
            cv_params_this = copy.deepcopy(cv_params)
            cv_params_this['grade'] = grade
            cv_params_this['reportCount'] = student_report_count_by_grade[grade]

            # Create the cover sheet task
            cover_tasks.append(bulk_pdf_cover_sheet.subtask(args=(cookie_value, cover_path, merged_path, cv_base_url,  # @UndefinedVariable
                                                                  cv_params_this, cookie_name, is_grayscale),
                                                            immutable=True))
            cover_sheets_by_grade[grade] = cover_path

    return cover_tasks, cover_sheets_by_grade


def _create_pdf_cover_merge_tasks(merged_pdfs_by_grade, cover_sheets_by_grade, directory_to_archive, pdf_base_dir):
    '''
    create pdf merge tasks
    '''
    merge_tasks = []
    if merged_pdfs_by_grade and cover_sheets_by_grade:
        for grade, merged_pdf_path in merged_pdfs_by_grade.items():
            # Get the desired final output path
            merged_name = os.path.basename(merged_pdf_path)
            merged_out_path = os.path.join(directory_to_archive, merged_name)

            # Put the two files together to merge
            file_names = [cover_sheets_by_grade[grade], merged_pdf_path]

            # Create the merge task
            merge_tasks.append(pdf_merge.subtask(args=(file_names, merged_out_path, pdf_base_dir), immutable=True))  # @UndefinedVariable
    return merge_tasks


def _has_context_for_pdf_request(state_code, student_id):
    '''
    Validates that user has context to student_id

    :param student_id:  guid(s) of the student(s)
    '''
    if type(student_id) is not list:
        student_id = [student_id]
    return check_context(RolesConstants.PII, state_code, student_id)


def _create_student_pdf_url(student_id, base_url, params, date_taken=None):
    params[Constants.STUDENTGUID] = student_id
    params[Constants.PDF] = "true"
    if date_taken is not None:
        params[Constants.DATETAKEN] = date_taken
    encoded_params = urllib.parse.urlencode(params)
    return base_url + "?%s" % encoded_params


def _start_bulk(archive_file_path, directory_to_archive, registration_id, gen_tasks, merge_tasks, cover_tasks,
                merge_covers_tasks, pdf_base_dir):
    '''
    entry point to start a bulk PDF generation request for one or more students
    it groups the generation of individual PDFs into a celery task group and then chains it to the next task to merge
    the files into one PDF, archive the PDF into a zip, and upload the zip to HPZ
    '''
    logger.info('Start bulk PDF generation')
    workflow = chain(group(gen_tasks),
                     group_separator.subtask(immutable=True),  # @UndefinedVariable
                     group(merge_tasks),
                     group_separator.subtask(immutable=True),  # @UndefinedVariable
                     group(cover_tasks),
                     group_separator.subtask(immutable=True),  # @UndefinedVariable
                     group(merge_covers_tasks),
                     archive.subtask(args=(archive_file_path, directory_to_archive), immutable=True),  # @UndefinedVariable
                     hpz_upload_cleanup.subtask(args=(archive_file_path, registration_id, pdf_base_dir), immutable=True))  # @UndefinedVariable
    workflow.apply_async()


def _get_cover_sheet_name(grade):
    return '{cover_sheet_name_prefix}{grade}.pdf'.format(cover_sheet_name_prefix=ServicesConstants.COVER_SHEET_NAME_PREFIX, grade=grade)


def _get_merged_pdf_name(school_name, grade, lang_code, grayscale):
    timestamp = str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))
    school_name = school_name.replace(' ', '')
    school_name = school_name[:15] if len(school_name) > 15 else school_name
    grade_val = '_grade_{grade}'.format(grade=grade) if grade != 'all' else ''
    name = 'student_reports_{school_name}{grade}_{timestamp}_{lang}'.format(school_name=school_name,
                                                                            grade=grade_val,
                                                                            timestamp=timestamp,
                                                                            lang=lang_code.lower())
    return name + ('.g.pdf' if grayscale else '.pdf')


def _get_archive_name(school_name, lang_code, grayscale):
    timestamp = str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))
    school_name = school_name.replace(' ', '')
    school_name = school_name[:15] if len(school_name) > 15 else school_name
    name = 'student_reports_{school_name}_{timestamp}_{lang}'.format(school_name=school_name,
                                                                     timestamp=timestamp,
                                                                     lang=lang_code.lower())
    return name + ('.g.zip' if grayscale else '.zip')


def _get_student_ids(state_code, district_id, school_id, asmt_type, params,
                     asmt_year=None, grade=None, student_ids=None):
    with EdCoreDBConnection(state_code=state_code) as connector:
        # Get handle to tables
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        if asmt_type == AssessmentType.INTERIM_ASSESSMENT_BLOCKS:
            fact_table = connector.get_table(Constants.FACT_BLOCK_ASMT_OUTCOME)
        else:
            fact_table = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)

        # Build select
        query = select_with_context([fact_table.c.student_id.label(Constants.STUDENT_ID),
                                     dim_student.c.first_name,
                                     dim_student.c.last_name],
                                    from_obj=[fact_table
                                              .join(dim_student, and_(fact_table.c.student_rec_id == dim_student.c.student_rec_id))
                                              .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_table.c.asmt_rec_id))],
                                    permission=RolesConstants.PII, state_code=state_code).distinct()

        # Add where clauses
        query = query.where(fact_table.c.state_code == state_code)
        query = query.where(and_(fact_table.c.school_id == school_id))
        query = query.where(and_(fact_table.c.district_id == district_id))
        query = query.where(and_(fact_table.c.rec_status == Constants.CURRENT))
        query = query.where(and_(fact_table.c.asmt_type == asmt_type))
        if grade is not None:
            query = query.where(and_(fact_table.c.asmt_grade == grade))
        if student_ids is not None:
            query = query.where(and_(fact_table.c.student_id.in_(student_ids)))
        elif asmt_year is not None:
            query = query.where(and_(dim_asmt.c.asmt_period_year == asmt_year))
        else:
            raise InvalidParameterError('Need one of effective_date or asmt_year')
        query = apply_filter_to_query(query, fact_table, dim_student, params)

        # Add order by clause
        query = query.order_by(dim_student.c.last_name).order_by(dim_student.c.first_name)

        # Return the result
        return connector.get_result(query)


def _get_school_name(state_code, district_id, school_id):
    with EdCoreDBConnection(state_code=state_code) as connector:
        # Get handle to tables
        dim_inst_hier = connector.get_table(Constants.DIM_INST_HIER)

        # Build select
        query = select([dim_inst_hier.c.school_name.label(Constants.SCHOOL_NAME)],
                       from_obj=[dim_inst_hier])

        # Add where clauses
        query = query.where(dim_inst_hier.c.state_code == state_code)
        query = query.where(and_(dim_inst_hier.c.district_id == district_id))
        query = query.where(and_(dim_inst_hier.c.school_id == school_id))
        query = query.where(and_(dim_inst_hier.c.rec_status == Constants.CURRENT))

        # Return the result
        results = connector.get_result(query)
        if len(results) == 1:
            logger.info('Bulk PDF : School name found')
            return results[0][Constants.SCHOOL_NAME]
        else:
            logger.error('Bulk PDF : School name not found')
            raise InvalidParameterError('School name cannot be found')
