'''
Created on Nov 11, 2015

@author: tosako
'''

from edschema.metadata.ed_metadata import generate_ed_metadata
from edschema.database.connector import DBConnection


config_namespace = 'migrate_public.db'


class EdMigratePublicConnection(DBConnection):
    '''
    DBConnector for EdMigrate Project
    This is used for source database connection for migration
    '''

    def __init__(self, tenant=None, state_code=None):
        super().__init__(name=self.get_datasource_name(tenant))

    @staticmethod
    def get_namespace():
        '''
        Returns the namespace of smarter database connection
        '''
        return config_namespace + '.'

    @staticmethod
    def get_datasource_name(tenant=None):
        '''
        Returns datasource name for a tenant
        '''
        if tenant is None:
            # Returns None will raise an Exception in base class
            return None
        return EdMigratePublicConnection.get_namespace() + tenant

    @staticmethod
    def get_db_config_prefix(tenant=None):
        '''
        Returns database config prefix based on tenant name
        '''
        if tenant is None:
            # Returns None will raise an Exception in base class
            return None
        return EdMigratePublicConnection.get_namespace() + tenant + '.'

    @staticmethod
    def generate_metadata(schema_name=None, bind=None):
        '''
        Generates metadata for edware
        '''
        return generate_ed_metadata(schema_name=schema_name, bind=bind)
