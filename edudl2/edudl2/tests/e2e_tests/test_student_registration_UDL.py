from edcore.database.stats_connector import StatsDBConnection
from edcore.database.utils.constants import UdlStatsConstants
from edudl2.tests.e2e_tests.database_helper import drop_target_schema
__author__ = 'smuhit'

import unittest
import shutil
import os
import subprocess
from time import sleep
from uuid import uuid4
from sqlalchemy.sql import select, and_, func
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process
from edudl2.database.udl2_connector import get_udl_connection, get_target_connection,\
    initialize_all_db
from edudl2.udl2 import message_keys as mk
from edudl2.udl2 import configuration_keys as ck
from edudl2.udl2.constants import Constants
import json
from edudl2.udl2.celery import udl2_conf, udl2_flat_conf

TENANT_DIR = '/opt/edware/zones/landing/arrivals/cat/ca_user/filedrop/'


class FTestStudentRegistrationUDL(unittest.TestCase):

    def setUp(self):
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "student_registration_data")
        self.student_reg_files = {
            'original_data': {
                'path': os.path.join(data_dir, 'test_sample_student_reg.tar.gz.gpg'),
                'num_records_in_data_file': 10,
                'num_records_in_json_file': 1,
                'test_student': {
                    'student_guid': '3333-AAAA-AAAA-AAAA',
                    'state_name_col': 'Dummy State',
                    'district_name_col': 'West Podunk School District',
                    'school_guid_col': '3333-3333-3333-3333',
                    'gender_col': 'female',
                    'dob_col': '1999-12-22',
                    'eth_hsp_col': True,
                    'sec504_col': False,
                    'year_col': 2015,
                    'reg_sys_id_col': '800b3654-4406-4a90-9591-be84b67054df'
                }
            },
            'data_for_different_test_center_than_original_data': {
                'path': os.path.join(data_dir, 'test_sample_student_reg_2.tar.gz.gpg'),
                'num_records_in_data_file': 3,
                'num_records_in_json_file': 1,
                'test_student': {
                    'student_guid': '3333-CCCC-CCCC-CCCC',
                    'state_name_col': 'Dummy State',
                    'district_name_col': 'West Podunk School District',
                    'school_guid_col': '3333-3333-3333-3333',
                    'gender_col': 'male',
                    'dob_col': '1998-01-23',
                    'eth_hsp_col': False,
                    'sec504_col': True,
                    'year_col': 2015,
                    'reg_sys_id_col': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
                }
            }
        }
        self.tenant_dir = TENANT_DIR
        self.load_type = Constants.LOAD_TYPE_STUDENT_REGISTRATION
        self.receive_requests = True
        initialize_all_db(udl2_conf, udl2_flat_conf)
        self.start_http_post_server()
        self.batches = []

    def tearDown(self):
        self.shutdown_http_post_server()
        if os.path.exists(self.tenant_dir):
            shutil.rmtree(self.tenant_dir)
        for batch in self.batches:
            try:
                drop_target_schema('cat', batch)
            except:
                pass

    #Validate the UDL process completed successfully
    def validate_successful_job_completion(self):
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            query = select([batch_table.c.udl_phase_step_status], and_(batch_table.c.guid_batch == self.batch_id, batch_table.c.udl_phase == 'UDL_COMPLETE'))
            result = connector.execute(query).fetchall()
            self.assertNotEqual(result, [])
            for row in result:
                status = row['udl_phase_step_status']
                self.assertEqual(status, mk.SUCCESS, 'UDL process did not complete successfully')

    #Validate the UDL process completed successfully
    def validate_stats_update(self, status):
        with StatsDBConnection() as conn:
            stats_table = conn.get_table('udl_stats')
            query = select([stats_table.c.batch_operation, stats_table.c.load_status, stats_table.c.snapshot_criteria]).where(stats_table.c.batch_guid == self.batch_id)
            result = conn.execute(query).fetchall()
            self.assertNotEqual(result, [])
            for row in result:
                operation = row['batch_operation']
                self.assertEqual(operation, 's')

                snapshot_criteria = json.loads(row['snapshot_criteria'])
                self.assertEqual(2, len(snapshot_criteria))
                self.assertEqual("800b3654-4406-4a90-9591-be84b67054df", snapshot_criteria['reg_system_id'])
                self.assertEqual(2015, snapshot_criteria['academic_year'])

                status = UdlStatsConstants.UDL_STATUS_INGESTED if status is mk.SUCCESS else UdlStatsConstants.UDL_STATUS_FAILED
                self.assertEqual(row['load_status'], status)

    #Validate that the load type received is student registration
    def validate_load_type(self):
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            query = select([batch_table.c.udl_phase_step_status, batch_table.c.load_type], and_(batch_table.c.guid_batch == self.batch_id, batch_table.c.udl_phase == 'udl2.W_get_load_type.task'))
            result = connector.execute(query).fetchall()
            self.assertNotEqual(result, [])
            for row in result:
                status = row['udl_phase_step_status']
                load = row['load_type']
                self.assertEqual(status, mk.SUCCESS)
                self.assertEqual(load, self.load_type, 'Not the expected load type.')

    #Validate the target table
    def validate_stu_reg_target_table(self, file_to_load):
        with get_target_connection('cat', self.batch_id) as conn:
            target_table = conn.get_table(Constants.SR_TARGET_TABLE)
            query = select([func.count()]).select_from(target_table)
            record_count = conn.execute(query).fetchall()[0][0]
            self.assertEqual(record_count, self.student_reg_files[file_to_load]['num_records_in_data_file'], 'Unexpected number of records in target table.')

    #Validate a student's data
    def validate_student_data(self, file_to_load):
        with get_target_connection('cat', self.batch_id) as conn:
            student = self.student_reg_files[file_to_load]['test_student']
            target_table = conn.get_table(Constants.SR_TARGET_TABLE)
            query = select([target_table.c.state_name, target_table.c.district_name, target_table.c.school_guid,
                            target_table.c.gender, target_table.c.birthdate, target_table.c.dmg_eth_hsp,
                            target_table.c.dmg_prg_504, target_table.c.academic_year, target_table.c.reg_system_id],
                           and_(target_table.c.student_guid == student['student_guid'], target_table.c.batch_guid == self.batch_id))
            result = conn.execute(query).fetchall()
            student_data_tuple = result[0]
            self.assertEquals(student_data_tuple[0], student['state_name_col'], 'State Name did not match')
            self.assertEquals(student_data_tuple[1], student['district_name_col'], 'District Name did not match')
            self.assertEquals(student_data_tuple[2], student['school_guid_col'], 'School Id did not match')
            self.assertEquals(student_data_tuple[3], student['gender_col'], 'Gender did not match')
            self.assertEquals(student_data_tuple[4], student['dob_col'], 'Date of Birth did not match')
            self.assertEquals(student_data_tuple[5], student['eth_hsp_col'], 'Hispanic Ethnicity should be true')
            self.assertEquals(student_data_tuple[6], student['sec504_col'], 'Section504 status should be false')
            self.assertEquals(student_data_tuple[7], student['year_col'], 'Academic Year did not match')
            self.assertEquals(student_data_tuple[8], student['reg_sys_id_col'], 'Test registration system\'s id did not match')

    # Validate that the notification to the callback url matches the status, with a certain number of retries attempted
    def validate_notification(self, expected_status, expected_error_codes, expected_retries):
        # If there are job notification retries, wait for job notification to finish.
        if expected_retries > 0:
            retry_interval = udl2_conf[ck.SR_NOTIFICATION_RETRY_INTERVAL]
            expected_duration = expected_retries * retry_interval
            max_wait_time = expected_duration + (retry_interval / 2)
            self.check_notification_completion(max_wait=max_wait_time)

        # Get the job results.
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            query = select([batch_table.c.udl_phase_step_status, batch_table.c.error_desc, batch_table.c.duration],
                           and_(batch_table.c.guid_batch == self.batch_id, batch_table.c.udl_phase == 'UDL_JOB_STATUS_NOTIFICATION'))
            result = connector.execute(query).fetchall()
            for row in result:
                notification_status = row['udl_phase_step_status']
                self.assertEqual(expected_status, notification_status)
                errors = row['error_desc']
                if expected_status == mk.FAILURE:
                    num_retries = errors.count(',')
                    self.assertEqual(expected_retries, num_retries, 'Incorrect number of retries')
                    for error_code in expected_error_codes:
                        self.assertTrue(error_code in errors)
                if expected_retries > 0:
                    duration = row['duration'].seconds
                    self.assertGreaterEqual(duration, expected_duration)

    #Run the UDL pipeline
    def run_udl_pipeline(self, file_to_load, max_wait=30):
        sr_file = self.copy_file_to_tmp(file_to_load)
        here = os.path.dirname(__file__)
        driver_path = os.path.join(here, "..", "..", "..", "scripts", "driver.py")
        command = "python {driver_path} -a {file_path} -g {guid}".format(driver_path=driver_path, file_path=sr_file, guid=self.batch_id)
        subprocess.call(command, shell=True)
        self.check_job_completion(max_wait)

    #Check the batch table periodically for completion of the UDL pipeline, waiting up to max_wait seconds
    def check_job_completion(self, max_wait=30):
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            query = select([batch_table.c.udl_phase],
                           and_(batch_table.c.guid_batch == self.batch_id, batch_table.c.udl_phase == 'UDL_COMPLETE'))
            timer = 0
            result = connector.execute(query).fetchall()
            while timer < max_wait and not result:
                sleep(0.25)
                timer += 0.25
                result = connector.execute(query).fetchall()
            print('Waited for', timer, 'second(s) for job to complete.')
            self.assertTrue(result, "No result retrieved")

    #Check the batch table periodically for completion of the UDL job status notification, waiting up to max_wait seconds
    def check_notification_completion(self, max_wait=30):
        with get_udl_connection() as connector:
            batch_table = connector.get_table(Constants.UDL2_BATCH_TABLE)
            query = select([batch_table.c.udl_phase],
                           and_(batch_table.c.guid_batch == self.batch_id, batch_table.c.udl_phase == 'UDL_JOB_STATUS_NOTIFICATION'))
            timer = 0
            result = connector.execute(query).fetchall()
            while timer < max_wait and not result:
                sleep(0.25)
                timer += 0.25
                result = connector.execute(query).fetchall()
            print('Waited for', timer, 'second(s) for notification to complete.')
            self.assertTrue(result, "No result retrieved")

    #Copy file to tenant directory
    def copy_file_to_tmp(self, file_to_load):
        if os.path.exists(self.tenant_dir):
            print("tenant dir already exists")
        else:
            os.makedirs(self.tenant_dir)
        return shutil.copy2(self.student_reg_files[file_to_load]['path'], self.tenant_dir)

    def test_udl_student_registration(self):
        # Run and verify first run of student registration data
        self.batch_id = str(uuid4())
        self.batches.append(self.batch_id)
        self.run_udl_pipeline('original_data')
        self.validate_successful_job_completion()
        self.validate_load_type()
        self.validate_stu_reg_target_table('original_data')
        self.validate_student_data('original_data')
        self.validate_notification(mk.SUCCESS, [], 0)
        self.validate_stats_update(mk.SUCCESS)

        # Run and verify second run of student registration data (different test registration than previous run)
        # Should retry notification twice, then succeed
        self.batch_id = str(uuid4())
        self.batches.append(self.batch_id)
        self.run_udl_pipeline('data_for_different_test_center_than_original_data', 45)
        self.validate_successful_job_completion()
        self.validate_stu_reg_target_table('data_for_different_test_center_than_original_data')
        self.validate_student_data('data_for_different_test_center_than_original_data')
        self.validate_notification(mk.SUCCESS, ['408', '408'], 2)

        # Run and verify second run of student registration data again
        # Should max out on retry attempts, then fail
        self.batch_id = str(uuid4())
        self.batches.append(self.batch_id)
        self.run_udl_pipeline('data_for_different_test_center_than_original_data', 45)
        self.validate_successful_job_completion()
        self.validate_stu_reg_target_table('data_for_different_test_center_than_original_data')
        self.validate_student_data('data_for_different_test_center_than_original_data')
        self.validate_notification(mk.FAILURE, ['408', '408', '408', '408', '408'], 4)

    def start_http_post_server(self):
        self.receive_requests = True
        try:
            self.proc = Process(target=self.run_http_post_server)
            self.proc.start()
        except Exception:
            pass

    def run_http_post_server(self):
        try:
            server_address = ('127.0.0.1', 8000)
            self.post_server = HTTPServer(server_address, HTTPPOSTHandler)
            self.post_server.timeout = 0.25
            while self.receive_requests:
                self.post_server.handle_request()
        finally:
            print('POST Service stop receiving requests.')

    def shutdown_http_post_server(self):
        try:
            self.receive_requests = False
            sleep(0.5)  # Give server time to stop listening
            self.proc.terminate()
            self.post_server.shutdown()
        except Exception:
            pass


# This class handles our HTTP POST requests with various responses
class HTTPPOSTHandler(BaseHTTPRequestHandler):
    response_count = 0
    response_codes = [201, 408, 408, 201, 408, 408, 408, 408, 408]

    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        self.send_response(HTTPPOSTHandler.response_codes[HTTPPOSTHandler.response_count])
        self.end_headers()
        HTTPPOSTHandler.response_count += 1

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    unittest.main()
