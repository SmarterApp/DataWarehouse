# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

'''
Created on Feb 14, 2014

@author: sravi
'''
from edschema.metadata.ed_metadata import generate_ed_metadata
from edschema.database.connector import DBConnection

config_namespace = 'migrate_source.db'


class EdMigrateSourceConnection(DBConnection):
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
        return EdMigrateSourceConnection.get_namespace() + tenant if tenant else EdMigrateSourceConnection.get_namespace()

    @staticmethod
    def get_db_config_prefix(tenant=None):
        '''
        Returns database config prefix based on tenant name
        '''
        return EdMigrateSourceConnection.get_namespace() + tenant + '.' if tenant else EdMigrateSourceConnection.get_namespace()

    @staticmethod
    def generate_metadata(schema_name=None, bind=None):
        '''
        Generates metadata for edware
        '''
        return generate_ed_metadata(schema_name=schema_name, bind=bind)
