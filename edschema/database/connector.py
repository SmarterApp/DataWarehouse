'''
Created on Jan 15, 2013

@author: tosako
'''

from database.interfaces import ConnectionBase
from edschema.ed_metadata import generate_ed_metadata
from sqlalchemy.engine import engine_from_config
from zope import interface, component
from zope.interface.declarations import implementer


class IDbUtil(interface.Interface):
    def get_engine(self):
        pass

    def get_metadata(self):
        pass


@implementer(IDbUtil)
class DbUtil:
    def __init__(self, prefix, configuration):
        self.__engine = engine_from_config(configuration, prefix, pool_size=20, max_overflow=10)
        self.__metadata = generate_ed_metadata(configuration['edschema.schema_name'])

    def get_engine(self):
        return self.__engine

    def get_metadata(self):
        return self.__metadata


class DBConnector(ConnectionBase):
    '''
    Inheritate this class if you are making a report class and need to access to database
    BaseReport is just managing session for your database connection and convert result to dictionary
    '''

    def __init__(self):
        dbUtil = component.queryUtility(IDbUtil)
        self.__engine = dbUtil.get_engine()
        self.__metadata = dbUtil.get_metadata()
        self.__connection = None

    def __del__(self):
        self.close_connection()

    # query and get result
    # Convert from result_set to dictionary.
    def get_result(self, query):
        result = self.__connection.execute(query)
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
        table = self.__metadata.tables['edware_star_20130129_1.dim_school']
        return table

    def open_connection(self):
        """
        return open connection
        """
        if self.__connection is None:
            self.__connection = self.__engine.connect()

        return self.__connection

    def close_connection(self):
        """
        closes the connection
        """
        if self.__connection is not None:
            self.__connection.close()
        self.__connection = None
