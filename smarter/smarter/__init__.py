from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.path import caller_package, caller_module, package_of
import sys
import edapi
import os
from edschema.ed_metadata import generate_ed_metadata
import pyramid
from zope import component
from database.connector import DbUtil, IDbUtil
from lesscss import LessCSS


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if 'smarter.PATH' in settings:
        os.environ['PATH'] += os.pathsep + settings['smarter.PATH']
    # TODO: Spike, pool_size, max_overflow, timeout

    config = Configurator(settings=settings)

    # zope registration
    engine = engine_from_config(settings, "sqlalchemy.", pool_size=20, max_overflow=10)
    metadata = generate_ed_metadata(settings['edschema.schema_name'])
    dbUtil = DbUtil(engine=engine, metadata=metadata)
    component.provideUtility(dbUtil, IDbUtil)

    # include add routes from edapi. Calls includeme
    config.include(edapi)

    # TODO symbolic link should be done in development mode only
    here = os.path.abspath(os.path.dirname(__file__))
    assets_dir = os.path.abspath(here + '/../assets')
    parent_assets_dir = os.path.abspath(here + '/../../assets')
    try:
        if not os.path.lexists(assets_dir):
            os.symlink(parent_assets_dir, assets_dir)
    except PermissionError:
        pass

    LessCSS(media_dir=parent_assets_dir + "/less", output_dir=parent_assets_dir + "/css", based=False)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('assets', '../assets', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('checkstatus', '/status')
    #
    config.add_route('comparing_populations', '/comparing_populations')
    config.add_route('test1', '/test1')
    config.add_route('template', '/template')
    config.add_route('generateComparePopulations', '/comPopResults')
    config.add_route('inputComparePopulations', '/comPop')
    config.add_route('generateComparePopulationsAl', '/comPopResultsAl')
    config.add_route('inputComparePopulationsAl', '/comPopAl')
    config.add_route('datatojson2', '/datatojson2')
    config.add_route('inputdata2', '/inputdata2')
    # splita's code
    config.add_route('comparepopulation', '/comparepopulation')
    config.add_route('getcomparepopulation', '/getcomparepopulation')

    # routing for individual student report
    config.add_route('indiv_student', '/indiv_student_report')
    # r routing for *bootstrapped* individual student report
    config.add_route('indiv_student_bootstrap', '/indiv_student_report_bootstrap')
    # routing for class report
    config.add_route('class_report', '/class_report')
    config.add_route('student_report', '/student_report')
    config.add_route('import', '/import')
    config.add_route('create', '/create')

    # scans smarter
    config.scan()

    return config.make_wsgi_app()
