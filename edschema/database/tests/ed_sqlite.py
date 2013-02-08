'''
Created on Feb 8, 2013

@author: tosako
'''
import os
from sqlalchemy.engine import create_engine
from database.connector import DbUtil, IDbUtil, DBConnector
from zope import component
from edschema.ed_metadata import generate_ed_metadata
import csv
from sqlalchemy.sql.expression import select


# create sqlite from static metadata
def create_sqlite():
    __engine = create_engine('sqlite:///:memory:')
    __metadata = generate_ed_metadata()
    __metadata.create_all(__engine)
    dbUtil = DbUtil(engine=__engine, metadata=__metadata)
    component.provideUtility(dbUtil, IDbUtil)


def generate_data():
    dbconnector = DBConnector()
    connection = dbconnector.open_connection()

    table = dbconnector.get_table('dim_district')

    here = os.path.abspath(os.path.dirname(__file__))

    with open(here + '/resources/dim_district.csv') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            connection.execute(table.insert().values(**row))
