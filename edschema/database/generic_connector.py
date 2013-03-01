'''
Created on Mar 1, 2013

@author: dip
'''
from sqlalchemy.engine import engine_from_config
from edschema.ed_metadata import generate_ed_metadata
from database.connector import DbUtil, IDbUtil
from zope import component


def setup_connection_from_ini(settings, prefix):
    '''
    Create a generic db connection
    '''
    engine = engine_from_config(settings, prefix)
    metadata = generate_ed_metadata(settings['edschema.schema_name'])

    # zope registration
    dbUtil = DbUtil(engine=engine, metadata=metadata)
    component.provideUtility(dbUtil, IDbUtil)
