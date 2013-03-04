'''
Created on Mar 1, 2013

@author: dip
'''
from sqlalchemy.schema import MetaData, Table, Column, Index
from sqlalchemy.types import String, UnicodeText, DateTime
from sqlalchemy.sql.expression import func


def generate_persistence(schema_name=None, bind=None):

    metadata = MetaData(schema=schema_name, bind=bind)

    user_session = Table('user_session', metadata,
                         Column('session_id', String(256), primary_key=True, nullable=True),
                         Column('session_context', UnicodeText, nullable=True),
                         Column('last_access', DateTime, default=func.now()),
                         Column('expiration', DateTime, default=func.now()),
                         )
    Index('user_session_idx', user_session.c.session_id, unique=True)

    return metadata
