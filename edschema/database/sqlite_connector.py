'''
Created on Feb 8, 2013

@author: tosako
'''
from sqlalchemy.engine import create_engine
from database.connector import DbUtil, IDbUtil
from zope import component
from edschema.ed_metadata import generate_ed_metadata
import sqlite3
from sqlalchemy.schema import MetaData
from sqlalchemy import event


# create sqlite from static metadata
def create_sqlite(force_foreign_keys=True, use_metadata_from_db=False, echo=False, metadata=None):
    __engine = create_engine('sqlite:///:memory:', connect_args={'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES}, native_datetime=True, echo=echo)

    if force_foreign_keys:
        event.listen(__engine, 'connect', __fk_on)

    __metadata = metadata
    if __metadata is None:
        __metadata = generate_ed_metadata()
    # create tables from static metadata
    __metadata.create_all(bind=__engine, checkfirst=False)

    if use_metadata_from_db:
        # since we want to test db creation, read metadata from sqlite
        __metadata = MetaData()
        __metadata.reflect(bind=__engine)

    dbUtil = DbUtil(engine=__engine, metadata=__metadata)
    component.provideUtility(dbUtil, IDbUtil)


def __fk_on(connection, rec):
    connection.execute('pragma foreign_keys=ON')


def destroy_sqlite():
    '''
    drop tables from memory
    and destory sqlite
    '''
    dbUtil = component.queryUtility(IDbUtil)
    __engine = dbUtil.get_engine()
    __metadata = dbUtil.get_metadata()
    __metadata.drop_all(bind=__engine, checkfirst=False)
    __engine.dispose()
    component.provideUtility(None, IDbUtil)


def delete_data():
    '''
    delete all data from the db
    '''
    dbUtil = component.queryUtility(IDbUtil)
    __engine = dbUtil.get_engine()
    __metadata = dbUtil.get_metadata()
    __metadata.drop_all(bind=__engine, checkfirst=False)
