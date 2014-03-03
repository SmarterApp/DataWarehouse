'''
Created on Jun 19, 2013

@author: tosako
'''
from sqlalchemy.schema import MetaData, Table, Column
from sqlalchemy.types import String, DateTime, BigInteger, Text
import datetime


def generate_stats_metadata(schema_name=None, bind=None):
    metadata = MetaData(schema=schema_name, bind=bind)
    udl_stats = Table('udl_stats', metadata,
                      Column('state_code', String(2), nullable=False),
                      Column('tenant', String(32), nullable=False),
                      Column('load_type', String(32), nullable=False),
                      Column('file_arrived', DateTime, nullable=False),
                      Column('load_start', DateTime, nullable=True),
                      Column('load_end', DateTime, nullable=True),
                      Column('load_status', String(32), nullable=False),
                      Column('batch_guid', String(50), nullable=False),
                      Column('record_loaded_count', BigInteger, nullable=True),
                      Column('last_pdf_task_requested', DateTime, nullable=True),
                      Column('last_pre_cached', DateTime, nullable=True)
                      )

    extract_stats = Table('extract_stats', metadata,
                          Column('request_guid', String(50), nullable=False),
                          Column('timestamp', DateTime, nullable=True),
                          Column('status', String(32), nullable=False),
                          Column('task_id', String(50), nullable=True),
                          Column('celery_task_id', String(50), nullable=True),
                          Column('info', Text, nullable=True)
                          )

    return metadata
