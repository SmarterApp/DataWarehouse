'''
Created on Jan 15, 2013

@author: tosako
'''

from database.interfaces import ConnectionBase
from zope import interface, component
from zope.interface.declarations import implementer
from sqlalchemy import Table
import logging


logger = logging.getLogger(__name__)


class IDbUtil(interface.Interface):
    def get_engine(self):
        pass

    def get_metadata(self):
        pass


@implementer(IDbUtil)
class DbUtil:
    def __init__(self, engine, metadata=None):
        self.__engine = engine
        self.__metadata = metadata

    def get_engine(self):
        return self.__engine

    def get_metadata(self):
        return self.__metadata


class DBConnection(ConnectionBase):
    '''
    Inheritate this class if you are making a report class and need to access to database
    BaseReport is just managing session for your database connection and convert result to dictionary
    '''
    def __init__(self, name=''):
        '''
        name is an empty string by default
        '''
        self.__name = name
        dbUtil = component.queryUtility(IDbUtil, name=name)
        engine = dbUtil.get_engine()
        self.__connection = engine.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, tb):
        return self.close_connection()

    def __del__(self):
        self.close_connection()

    # query and get result
    # Convert from result_set to dictionary.
    def get_result(self, query):
        result = self.execute(query)
        result_rows = []

        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                result_row = {}
                for key in row.keys():
                    result_row[key] = row[key]
                result_rows.append(result_row)
        return result_rows

    # return Table Metadata
    def get_table(self, table_name):
        return Table(table_name, self.get_metadata())

    def get_metadata(self):
        dbUtil = component.queryUtility(IDbUtil, name=self.__name)
        return dbUtil.get_metadata()

    def execute(self, statement, *multiparams, **params):
        return self.__connection.execute(statement, *multiparams, **params)

    def get_transaction(self):
        """
        return open connection
        """
        return self.__connection.begin()

    def close_connection(self):
        """
        closes the connection
        """
        if self.__connection is not None:
            self.__connection.close()
        self.__connection = None
