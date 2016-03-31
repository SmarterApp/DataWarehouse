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
Created on Jan 31, 2014

@author: bpatel
'''
import subprocess
import os
import shutil
from uuid import uuid4
from edudl2.database.udl2_connector import get_target_connection, get_udl_connection
from sqlalchemy.sql import select
from time import sleep
from sqlalchemy.sql.expression import and_
from edudl2.udl2.constants import Constants
from edudl2.tests.e2e_tests import UDLE2ETestCase


TENANT_DIR = '/opt/edware/zones/landing/arrivals/cat/ca_user/filedrop/'
UDL2_DEFAULT_CONFIG_PATH_FILE = '/opt/edware/conf/udl2_conf.py'
path = '/opt/edware/zones/landing/work/ca'
FACT_TABLE = 'fact_asmt_outcome_vw'


class ValidateSchemaChange(UDLE2ETestCase):

    def setUp(self):
        self.archived_file = self.require_gpg_file('test_source_file_tar_gzipped')
        self.tenant_dir = TENANT_DIR
        self.guid_batch_id = str(uuid4())

    def tearDown(self):
        if os.path.exists(self.tenant_dir):
            shutil.rmtree(self.tenant_dir)
        #drop_target_schema('cat', self.guid_batch_id)

    # Run the pipeline
    def run_udl_pipeline(self):
        arch_file = self.copy_file_to_tmp()
        here = os.path.dirname(__file__)
        driver_path = os.path.join(here, "..", "..", "..", "scripts", "driver.py")
        command = "python {driver_path} -a {file_path} -g {guid}".format(driver_path=driver_path, file_path=arch_file, guid=self.guid_batch_id)
        subprocess.call(command, shell=True)
        self.check_job_completion()

    #Copy file to tenant folder
    def copy_file_to_tmp(self):
        if not os.path.exists(self.tenant_dir):
            os.makedirs(self.tenant_dir)
        return shutil.copy2(self.archived_file, self.tenant_dir)

    #Check the batch table periodically for completion of the UDL pipeline, waiting up to max_wait seconds
    def check_job_completion(self, max_wait=30):
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            query = select([batch_table.c.udl_phase], and_(batch_table.c.guid_batch == self.guid_batch_id, batch_table.c.udl_phase == 'UDL_COMPLETE'))
            timer = 0
            result = connector.execute(query).fetchall()
            while timer < max_wait and result == []:
                sleep(0.25)
                timer += 0.25
                result = connector.execute(query).fetchall()

    #Validate that for given batch guid data loded on star schema and student_rec_id in not -1
    def validate_edware_database(self):
        with get_target_connection('cat', self.guid_batch_id) as ed_connector:
            edware_table = ed_connector.get_table(FACT_TABLE)
            output = select([edware_table.c.batch_guid]).where(edware_table.c.batch_guid == self.guid_batch_id)
            output_val = select([edware_table.c.student_rec_id]).where(edware_table.c.batch_guid == self.guid_batch_id)
            output_data = ed_connector.execute(output).fetchall()
            output_data1 = ed_connector.execute(output_val).fetchall()
            # Velidate that student_rec_id not containing -1
            self.assertNotIn(-1, output_data1, "Student rec id in not -1 in fact_asmt")
            # Velidate that data loaded into fact_Table after pipeline
            row_count = len(output_data)
            self.assertGreater(row_count, 1, "Data is loaded to star shema")
            truple_str = (self.guid_batch_id, )
            self.assertIn(truple_str, output_data, "assert successful")

            #TODO add dim student verification
            #dim_student = ed_connector.get_table(DIM_STUDENT)
            #student_table = select([dim_student.c.student_rec_id, dim_student.c.student_id])
            #output_data3 = ed_connector.execute(student_table).fetchall()

    def test_schema_change(self):
        self.run_udl_pipeline()
        self.validate_edware_database()
