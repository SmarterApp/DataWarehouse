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
Created on Sep 10, 2013

@author: bpatel
'''
import subprocess
import os
import shutil
from edudl2.database.udl2_connector import get_udl_connection, get_target_connection
from sqlalchemy.sql import select, and_
from time import sleep
from uuid import uuid4
from edudl2.tests.e2e_tests.database_helper import drop_target_schema
from edudl2.udl2.constants import Constants
from edudl2.tests.e2e_tests import UDLE2ETestCase


class ValidateTableData(UDLE2ETestCase):

    def setUp(self):
        self.tenant_dir = '/opt/edware/zones/landing/arrivals/nc/edware_user/filedrop/'
        self.archived_file = self.require_gpg_file('test_source_file_tar_gzipped')
        self.guid_batch_id = str(uuid4())

    def tearDown(self):
        if os.path.exists(self.tenant_dir):
            shutil.rmtree(self.tenant_dir)
        drop_target_schema('nc', self.guid_batch_id)

    def empty_batch_table(self):
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            result = connector.execute(batch_table.delete())
            query = select([batch_table])
            result1 = connector.execute(query).fetchall()
            number_of_row = len(result1)
            self.assertEqual(number_of_row, 0)

    def run_udl_pipeline(self):
        arch_file = self.copy_file_to_tmp()
        here = os.path.dirname(__file__)
        driver_path = os.path.join(here, "..", "..", "..", "scripts", "driver.py")
        command = "python {driver_path} -a {file_name} -g {guid}".format(driver_path=driver_path, file_name=arch_file, guid=self.guid_batch_id)
        subprocess.call(command, shell=True)
        self.check_job_completion()

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

    def connect_verify_db(self):
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            query = select([batch_table])
            result = connector.execute(query).fetchall()
            output = select([batch_table.c.udl_phase_step_status], and_(batch_table.c.udl_phase == 'UDL_COMPLETE', batch_table.c.guid_batch == self.guid_batch_id))
            output_data = connector.execute(output).fetchall()
            tuple_str = [('SUCCESS',)]
            self.assertEqual(tuple_str, output_data)

    def test_benchmarking_data(self):
        self.empty_batch_table()
        self.run_udl_pipeline()
        self.connect_verify_db()
        self.verify_multi_tenancy()

    def copy_file_to_tmp(self):
        if not os.path.exists(self.tenant_dir):
            os.makedirs(self.tenant_dir)

        return shutil.copy2(self.archived_file, self.tenant_dir)

    def verify_multi_tenancy(self):
        with get_target_connection('nc', self.guid_batch_id) as ed_connector:
            edware_table = ed_connector.get_table('dim_asmt')
            query_dim_table = select([edware_table])
            result_dim_table = ed_connector.execute(query_dim_table).fetchall()
            self.assertEquals(len(result_dim_table), 1, "Data not loaded into preprod")
