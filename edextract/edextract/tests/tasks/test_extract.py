'''
Created on Nov 7, 2013

@author: dip
'''
import unittest
import mock

import tempfile
import os
import shutil
import json
import csv
from zipfile import ZipFile
from collections import OrderedDict

from edcore.tests.utils.unittest_with_stats_sqlite import Unittest_with_stats_sqlite
from edcore.tests.utils.unittest_with_edcore_sqlite import (Unittest_with_edcore_sqlite, UnittestEdcoreDBConnection,
                                                            get_unittest_tenant_name)
from sqlalchemy.sql.expression import select
from edextract.celery import setup_celery
from edextract.tasks.constants import Constants as TaskConstants
from celery.canvas import group
from edextract.exceptions import ExtractionError
from edextract.settings.config import setup_settings
from edextract.tasks.constants import ExtractionDataType
from edextract.tasks.extract import (generate_extract_file_tasks, generate_extract_file, archive, archive_with_encryption, remote_copy,
                                     prepare_path)
from edextract.exceptions import RemoteCopyError


class TestExtractTask(Unittest_with_edcore_sqlite, Unittest_with_stats_sqlite):

    def setUp(self):
        here = os.path.abspath(os.path.dirname(__file__))
        gpg_home = os.path.abspath(os.path.join(here, "..", "..", "..", "..", "config", "gpg"))
        settings = {'extract.celery.BROKER_URL': 'memory',
                    'extract.gpg.keyserver': None,
                    'extract.gpg.homedir': gpg_home,
                    'extract.gpg.public_key.cat': 'kswimberly@amplify.com',
                    'extract.celery.CELERY_ALWAYS_EAGER': 'True',
                    'extract.retries_allowed': '1',
                    'extract.retry_delay': '60'
                    }
        setup_celery(settings)
        setup_settings(settings)
        self._tenant = get_unittest_tenant_name()
        self.__files = ['a.txt', 'b.txt', 'c.txt']
        self.__tmp_dir = tempfile.mkdtemp('file_archiver_test')
        self.__tmp_zip = os.path.join(tempfile.mkdtemp('zip'), 'test.zip')
        for file in self.__files:
            with open(os.path.join(self.__tmp_dir, file), "w") as f:
                f.write('hello ' + file)

        self.statistics_headers = ['State', 'District', 'School', 'Category', 'Value', 'AY2014 Count', 'AY2014 Percent of Total',
                                   'AY2015 Count', 'AY2015 Percent of Total', 'Change in Count', 'Percent Difference in Count',
                                   'Change in Percent of Total', 'AY2015 Matched IDs to AY2014 Count', 'AY2015 Matched IDs Percent of AY2014 Count']
        self.completion_headers = ['State', 'District', 'School', 'Grade', 'Category', 'Value', 'Assessment Subject',
                                   'Assessment Type', 'Assessment Date', 'Academic Year', 'Count of Students Registered',
                                   'Count of Students Assessed', 'Percent of Students Assessed']

    @classmethod
    def setUpClass(cls):
        Unittest_with_edcore_sqlite.setUpClass()
        Unittest_with_stats_sqlite.setUpClass()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir)
        shutil.rmtree(os.path.dirname(self.__tmp_zip))

    def test_generate(self):
        pass

    def test_archive(self):
        open(self.__tmp_zip, 'wb').write(archive('req_id', self.__tmp_dir))
        zipfile = ZipFile(self.__tmp_zip, "r")
        namelist = zipfile.namelist()
        self.assertEqual(3, len(namelist))
        self.assertIn('a.txt', namelist)
        self.assertIn('b.txt', namelist)
        self.assertIn('c.txt', namelist)

        file_a = zipfile.read('a.txt')
        self.assertEqual(b'hello a.txt', file_a)
        file_b = zipfile.read('b.txt')
        self.assertEqual(b'hello b.txt', file_b)
        file_c = zipfile.read('c.txt')
        self.assertEqual(b'hello c.txt', file_c)
        zipfile.close()

    def test_generate_csv_no_tenant(self):
        output = '/tmp/unittest.csv.gz.pgp'
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.QUERY_CSV,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.TASK_QUERY: None
        }
        result = generate_extract_file.apply(args=[None, '0', task])    # @UndefinedVariable
        result.get()
        self.assertFalse(os.path.exists(output))

    def test_generate_csv(self):
        with UnittestEdcoreDBConnection() as connection:
            dim_asmt = connection.get_table('dim_asmt')
            query = select([dim_asmt.c.asmt_guid, dim_asmt.c.asmt_period], from_obj=[dim_asmt])
            query = query.where(dim_asmt.c.asmt_guid == '22')
        output = os.path.join(self.__tmp_dir, 'asmt.csv')
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.QUERY_CSV,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.TASK_QUERY: query
        }
        result = generate_extract_file.apply(args=[self._tenant, 'request_id', task])    # @UndefinedVariable
        result.get()
        self.assertTrue(os.path.exists(output))
        csv_data = []
        with open(output) as out:
            data = csv.reader(out)
            for row in data:
                csv_data.append(row)
        self.assertEqual(len(csv_data), 2)
        self.assertEqual(csv_data[0], ['asmt_guid', 'asmt_period'])
        self.assertEqual(csv_data[1], ['22', 'Spring 2016'])

    def test_generate_csv_with_bad_file(self):
        with UnittestEdcoreDBConnection() as connection:
            dim_asmt = connection.get_table('dim_asmt')
            query = select([dim_asmt.c.asmt_guid], from_obj=[dim_asmt])
            query = query.where(dim_asmt.c.asmt_guid == '2123122')
        output = 'C:'
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.QUERY_CSV,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.TASK_QUERY: query
        }
        result = generate_extract_file.apply(args=[self._tenant, 'request_id', task])    # @UndefinedVariable
        self.assertRaises(ExtractionError, result.get,)

    def test_generate_json(self):
        with UnittestEdcoreDBConnection() as connection:
            dim_asmt = connection.get_table('dim_asmt')
            query = select([dim_asmt.c.asmt_guid], from_obj=[dim_asmt])
            query = query.where(dim_asmt.c.asmt_guid == '22')
            output = os.path.join(self.__tmp_dir, 'asmt.json')
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.QUERY_JSON,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.TASK_QUERY: query
        }
        results = generate_extract_file.apply(args=[self._tenant, 'request_id', task])    # @UndefinedVariable
        results.get()
        self.assertTrue(os.path.exists(output))
        with open(output) as out:
            data = json.load(out)
        self.assertEqual(data['asmt_guid'], '22')

    def test_generate_json_not_writable(self):
        with UnittestEdcoreDBConnection() as connection:
            dim_asmt = connection.get_table('dim_asmt')
            query = select([dim_asmt.c.asmt_guid], from_obj=[dim_asmt])
            query = query.where(dim_asmt.c.asmt_guid == '22')
        output = os.path.join('', 'asmt.json')
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.QUERY_JSON,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.TASK_QUERY: query
        }
        results = generate_extract_file.apply(args=[self._tenant, 'request_id', task])    # @UndefinedVariable
        self.assertRaises(ExtractionError, results.get)

    def test_generate_json_with_no_results(self):
        with UnittestEdcoreDBConnection() as connection:
            dim_asmt = connection.get_table('dim_asmt')
            query = select([dim_asmt.c.asmt_guid], from_obj=[dim_asmt])
            query = query.where(dim_asmt.c.asmt_guid == '2123122')
        output = os.path.join(self.__tmp_dir, 'asmt.json')
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.QUERY_JSON,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.TASK_QUERY: query
        }
        results = generate_extract_file.apply(args=[self._tenant, 'request_id', task])    # @UndefinedVariable
        results.get()
        self.assertTrue(os.path.exists(output))
        statinfo = os.stat(output)
        self.assertEqual(0, statinfo.st_size)

    def test_generate_json_with_bad_file(self):
        with UnittestEdcoreDBConnection() as connection:
            dim_asmt = connection.get_table('dim_asmt')
            query = select([dim_asmt.c.asmt_guid], from_obj=[dim_asmt])
            query = query.where(dim_asmt.c.asmt_guid == '2123122')
        output = 'C:'
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.QUERY_JSON,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.TASK_QUERY: query
        }
        results = generate_extract_file.apply(args=[self._tenant, 'request_id', task])    # @UndefinedVariable
        self.assertRaises(ExtractionError, results.get)

    def test_generate_sr_statistics_csv_success(self):
        output = os.path.join(self.__tmp_dir, 'stureg_stat.csv')
        task = self.construct_extract_args_sr_stat(ExtractionDataType.SR_STATISTICS, 2016, output)
        result = generate_extract_file.apply(args=[self._tenant, 'request_id', task])
        result.get()
        self.assertTrue(os.path.exists(output))
        csv_data = []
        with open(output) as out:
            data = csv.reader(out)
            for row in data:
                csv_data.append(row)
        #Data has 15 edOrgs
        self.assertEqual(len(csv_data), 421)
        self.assertEqual(csv_data[0], ['State', 'District', 'School', 'Category', 'Value', 'AY2015 Count', 'AY2015 Percent of Total',
                                       'AY2016 Count', 'AY2016 Percent of Total', 'Change in Count', 'Percent Difference in Count',
                                       'Change in Percent of Total', 'AY2016 Matched IDs to AY2015 Count', 'AY2016 Matched IDs Percent of AY2015 Count'])

    def test_generate_sr_statistics_csv_no_tenant(self):
        output = os.path.join(self.__tmp_dir, 'stureg_stat.csv')
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.SR_STATISTICS,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.ACADEMIC_YEAR: 2014
        }
        result = generate_extract_file.apply(args=[None, 'request_id', task])
        result.get()
        self.assertFalse(os.path.exists(output))

    def test_generate_sr_statistics_csv_bad_file(self):
        output = 'C:'
        task = {
            TaskConstants.EXTRACTION_DATA_TYPE: ExtractionDataType.SR_STATISTICS,
            TaskConstants.TASK_TASK_ID: 'task_id',
            TaskConstants.TASK_FILE_NAME: output,
            TaskConstants.ACADEMIC_YEAR: 2014
        }
        result = generate_extract_file.apply(args=[self._tenant, 'request_id', task])
        self.assertRaises(ExtractionError, result.get,)

    def test_generate_extract_file_tasks_asmt_json_request(self):
        # Have to use OrderedDict here to ensure order in results.
        tasks = [OrderedDict([(TaskConstants.EXTRACTION_DATA_TYPE, ExtractionDataType.QUERY_JSON),
                              (TaskConstants.TASK_FILE_NAME, 'abc'),
                              (TaskConstants.TASK_QUERY, 'abc'),
                              (TaskConstants.TASK_TASK_ID, 'abc')])]
        tasks_group = generate_extract_file_tasks(self._tenant, 'request', tasks)
        self.assertIsInstance(tasks_group, group)
        self.assertEqual("tasks.extract.generate_extract_file('tomcat', 'request', OrderedDict([('extraction_data_type', 'QueryJSONExtract'), ('file_name', 'abc'), ('query', 'abc'), ('task_id', 'abc')]))", str(tasks_group.kwargs['tasks'][0]))

    def test_generate_extract_file_tasks_asmt_csv_request(self):
        # Have to use OrderedDict here to ensure order in results.
        tasks = [OrderedDict([(TaskConstants.EXTRACTION_DATA_TYPE, ExtractionDataType.QUERY_CSV),
                              (TaskConstants.TASK_FILE_NAME, 'abc'),
                              (TaskConstants.TASK_QUERY, 'abc'),
                              (TaskConstants.TASK_TASK_ID, 'abc')])]
        tasks_group = generate_extract_file_tasks(self._tenant, 'request', tasks)
        self.assertIsInstance(tasks_group, group)
        self.assertEqual("tasks.extract.generate_extract_file('tomcat', 'request', OrderedDict([('extraction_data_type', 'QueryCSVExtract'), ('file_name', 'abc'), ('query', 'abc'), ('task_id', 'abc')]))", str(tasks_group.kwargs['tasks'][0]))

    def test_route_tasks_json_request_asmt_multi_requests(self):
        # Have to use OrderedDicts here to ensure order in results.
        tasks = [OrderedDict([(TaskConstants.EXTRACTION_DATA_TYPE, ExtractionDataType.QUERY_JSON),
                              (TaskConstants.TASK_FILE_NAME, 'abc'),
                              (TaskConstants.TASK_QUERY, 'abc'),
                              (TaskConstants.TASK_TASK_ID, 'abc')]),
                 OrderedDict([(TaskConstants.EXTRACTION_DATA_TYPE, ExtractionDataType.QUERY_CSV),
                              (TaskConstants.TASK_FILE_NAME, 'def'),
                              (TaskConstants.TASK_QUERY, 'def'),
                              (TaskConstants.TASK_TASK_ID, 'def')])]
        tasks_group = generate_extract_file_tasks(self._tenant, 'request', tasks)
        self.assertIsInstance(tasks_group, group)
        self.assertEqual("tasks.extract.generate_extract_file('tomcat', 'request', OrderedDict([('extraction_data_type', 'QueryJSONExtract'), ('file_name', 'abc'), ('query', 'abc'), ('task_id', 'abc')]))", str(tasks_group.kwargs['tasks'][0]))
        self.assertEqual("tasks.extract.generate_extract_file('tomcat', 'request', OrderedDict([('extraction_data_type', 'QueryCSVExtract'), ('file_name', 'def'), ('query', 'def'), ('task_id', 'def')]))", str(tasks_group.kwargs['tasks'][1]))

    def test_generate_extract_file_tasks_sr_statistics_request(self):
        # Have to use OrderedDict here to ensure order in results.
        tasks = [OrderedDict([(TaskConstants.EXTRACTION_DATA_TYPE, ExtractionDataType.SR_STATISTICS),
                              (TaskConstants.TASK_FILE_NAME, 'abc'),
                              (TaskConstants.TASK_QUERY, 'abc'),
                              (TaskConstants.TASK_TASK_ID, 'abc')])]
        tasks_group = generate_extract_file_tasks(self._tenant, 'request', tasks)
        self.assertIsInstance(tasks_group, group)
        self.assertEqual("tasks.extract.generate_extract_file('tomcat', 'request', OrderedDict([('extraction_data_type', 'StudentRegistrationStatisticsReportCSV'), ('file_name', 'abc'), ('query', 'abc'), ('task_id', 'abc')]))", str(tasks_group.kwargs['tasks'][0]))

    def test_archive_with_encryption(self):
        files = ['test_0.csv', 'test_1.csv', 'test.json']
        with tempfile.TemporaryDirectory() as _dir:
            csv_dir = os.path.join(_dir, 'csv')
            os.mkdir(csv_dir)
            gpg_file = os.path.join(_dir, 'gpg', 'output.gpg')
            os.mkdir(os.path.dirname(gpg_file))
            for file in files:
                with open(os.path.join(csv_dir, file), 'a') as f:
                    f.write(file)

            request_id = '1'
            recipients = 'kswimberly@amplify.com'
            result = archive_with_encryption.apply(args=[request_id, recipients, gpg_file, csv_dir])    # @UndefinedVariable
            result.get()
            self.assertTrue(os.path.exists(gpg_file))

    def test_archive_with_encryption_no_recipients(self):
        files = ['test_0.csv', 'test_1.csv', 'test.json']
        with tempfile.TemporaryDirectory() as _dir:
            csv_dir = os.path.join(_dir, 'csv')
            os.mkdir(csv_dir)
            gpg_file = os.path.join(_dir, 'gpg', 'output.gpg')
            os.mkdir(os.path.dirname(gpg_file))
            for file in files:
                with open(os.path.join(csv_dir, file), 'a') as f:
                    f.write(file)

            request_id = '1'
            recipients = 'nobody@amplify.com'
            result = archive_with_encryption.apply(args=[request_id, recipients, gpg_file, csv_dir])    # @UndefinedVariable
            self.assertRaises(ExtractionError, result.get)

    def test_remote_copy_success(self):
        request_id = '1'
        tenant = 'es'
        gatekeeper = 'foo'
        sftp_info = ['128.0.0.2', 'nobody', '/dev/null']
        with tempfile.TemporaryDirectory() as _dir:
            src_file_name = os.path.join(_dir, 'src.txt')
            open(src_file_name, 'w').close()
            with mock.patch('edextract.tasks.extract.copy') as mock_copy:
                remote_copy.apply(args=[request_id, src_file_name, tenant, gatekeeper, sftp_info], kwargs={'timeout': 3})     # @UndefinedVariable
                mock_copy.assert_called_with(src_file_name, '128.0.0.2', 'es', 'foo', 'nobody', '/dev/null', timeout=3)

    @unittest.skip
    def test_remote_copy_failure(self):
        request_id = '1'
        tenant = 'es'
        gatekeeper = 'foo'
        sftp_info = ['128.0.0.2', 'nobody', '/dev/null']
        with tempfile.TemporaryDirectory() as _dir:
            src_file_name = os.path.join(_dir, 'src.txt')
            open(src_file_name, 'w').close()
            with mock.patch('edextract.tasks.extract.copy') as mock_copy:
                mock_copy.side_effect = RemoteCopyError()
                result = remote_copy.apply(args=[request_id, src_file_name, tenant, gatekeeper, sftp_info], kwargs={'timeout': 3})     # @UndefinedVariable
                self.assertRaises(ExtractionError, result.get)

    def test_prepare_path(self):
        tmp_dir = tempfile.mkdtemp()
        shutil.rmtree(tmp_dir, ignore_errors=True)
        self.assertFalse(os.path.exists(tmp_dir))
        prepare_path.apply(args=["id", [tmp_dir]]).get()    # @UndefinedVariable
        self.assertTrue(os.path.exists(tmp_dir))

    def construct_extract_args(self, extraction_type, academic_year, output):
        current_year = str(academic_year)
        previous_year = str(academic_year - 1)
        query = 'SELECT * FROM student_reg WHERE academic_year == {current_year} OR academic_year == {previous_year}'\
            .format(current_year=current_year, previous_year=previous_year)
        headers = self.construct_statistics_headers(academic_year) if extraction_type == ExtractionDataType.SR_STATISTICS \
            else self.completion_headers
        extract_args = {TaskConstants.EXTRACTION_DATA_TYPE: extraction_type,
                        TaskConstants.TASK_TASK_ID: 'task_id',
                        TaskConstants.ACADEMIC_YEAR: academic_year,
                        TaskConstants.TASK_FILE_NAME: output,
                        TaskConstants.TASK_QUERY: query,
                        TaskConstants.CSV_HEADERS: headers
                        }

        return extract_args

    def construct_extract_args_sr_stat(self, extraction_type, academic_year, output):
        current_year = str(academic_year)
        previous_year = str(academic_year - 1)
        academic_year_query = 'SELECT * FROM student_reg WHERE academic_year == {current_year} OR academic_year == {previous_year}'\
            .format(current_year=current_year, previous_year=previous_year)
        match_query = 'SELECT cr.state_code, p.state_code as prev_state_code , cr.state_name, cr.district_guid, p.district_guid as prev_district_guid ,' \
                      'cr.district_name, cr.school_guid, p.school_guid as prev_school_guid , cr.school_name, cr.gender, p.gender as prev_gender , ' \
                      'cr.enrl_grade, p.enrl_grade as prev_enrl_grade , cr.dmg_eth_hsp, p.dmg_eth_hsp as prev_dmg_eth_hsp , cr.dmg_eth_ami, ' \
                      'p.dmg_eth_ami as prev_dmg_eth_ami , cr.dmg_eth_asn, p.dmg_eth_asn as prev_dmg_eth_asn ,cr.dmg_eth_blk, p.dmg_eth_blk as prev_dmg_eth_blk , ' \
                      'cr.dmg_eth_pcf, p.dmg_eth_pcf as prev_dmg_eth_pcf ,cr.dmg_eth_wht, p.dmg_eth_wht as prev_dmg_eth_wht , cr.dmg_prg_iep, ' \
                      'p.dmg_prg_iep as prev_dmg_prg_iep , cr.dmg_prg_lep, p.dmg_prg_lep as prev_dmg_prg_lep ,cr.dmg_prg_504, ' \
                      'p.dmg_prg_504 as prev_dmg_prg_504 , cr.dmg_sts_ecd, p.dmg_sts_ecd as prev_dmg_sts_ecd , cr.dmg_sts_mig, p.dmg_sts_mig as prev_dmg_sts_mig ,' \
                      ' cr.dmg_multi_race, p.dmg_multi_race as prev_dmg_multi_race , cr.academic_year ' \
                      'FROM student_reg cr inner join student_reg p on cr.student_guid = p.student_guid WHERE cr.academic_year == {current_year} AND p.academic_year == {previous_year}'\
            .format(current_year=current_year, previous_year=previous_year)
        headers = self.construct_statistics_headers(academic_year) if extraction_type == ExtractionDataType.SR_STATISTICS \
            else self.completion_headers
        extract_args = {TaskConstants.EXTRACTION_DATA_TYPE: extraction_type,
                        TaskConstants.TASK_TASK_ID: 'task_id',
                        TaskConstants.ACADEMIC_YEAR: academic_year,
                        TaskConstants.TASK_FILE_NAME: output,
                        TaskConstants.TASK_ACADEMIC_YEAR_QUERY: academic_year_query,
                        TaskConstants.TASK_MATCH_ID_QUERY: match_query,
                        TaskConstants.CSV_HEADERS: headers
                        }

        return extract_args

    def construct_statistics_headers(self, academic_year):
        current_year = str(academic_year)
        previous_year = str(academic_year - 1)
        statistics_headers = ['State', 'District', 'School', 'Category', 'Value',
                              'AY{previous_year} Count'.format(previous_year=previous_year),
                              'AY{previous_year} Percent of Total'.format(previous_year=previous_year),
                              'AY{current_year} Count'.format(current_year=current_year),
                              'AY{current_year} Percent of Total'.format(current_year=current_year), 'Change in Count',
                              'Percent Difference in Count', 'Change in Percent of Total',
                              'AY{current_year} Matched IDs to AY{previous_year} Count'.format(current_year=current_year, previous_year=previous_year),
                              'AY{current_year} Matched IDs Percent of AY{previous_year} Count'.format(current_year=current_year, previous_year=previous_year)]

        return statistics_headers


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
