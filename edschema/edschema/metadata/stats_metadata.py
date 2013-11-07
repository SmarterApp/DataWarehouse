'''
Created on Jun 19, 2013

@author: tosako
'''
from sqlalchemy.schema import MetaData, Table, Column
from sqlalchemy.types import String, DateTime, BigInteger
import datetime


def generate_stats_metadata(schema_name=None, bind=None):
    metadata = MetaData(schema=schema_name, bind=bind)
    udl_stats = Table('udl_stats', metadata,
                      Column('state_code', String(2), nullable=False),
                      Column('tenant', String(32), nullable=True),
                      Column('load_start', DateTime, nullable=False),
                      Column('load_end', DateTime, nullable=True),
                      Column('load_status', String(32), nullable=False),
                      Column('batch_guid', String(50), nullable=True),
                      Column('record_loaded_count', BigInteger, nullable=False),
                      Column('last_pdf_task_requested', DateTime, nullable=True, default=datetime.datetime.strptime('20000101000000', '%Y%m%d%H%M%S')),
                      Column('last_pre_cached', DateTime, nullable=True, default=datetime.datetime.strptime('20000101000000', '%Y%m%d%H%M%S'))
                      )

    extract_stats = Table('extract_stats', metadata,
                          Column('tenant', String(32), nullable=False),
                          Column('user_guid', String(50), nullable=False),
                          Column('request_guid', String(50), nullable=False),
                          Column('extract_start', DateTime, nullable=True),
                          Column('extract_end', DateTime, nullable=True),
                          Column('extract_status', String(32), nullable=False),
                          Column('task_id', String(50), nullable=True),
                          Column('celery_task_id', String(50), nullable=True),
                          Column('extract_params', String(256), nullable=False)
                          )
    return metadata
