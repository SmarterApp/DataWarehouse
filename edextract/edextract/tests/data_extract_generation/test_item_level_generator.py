__author__ = 'nestep'

"""
Module containing assessment item-level generator unit tests.
"""

import csv
import os
import shutil
import tempfile

from sqlalchemy.sql.expression import and_, select

from edcore.security.tenant import set_tenant_map
from edcore.tests.utils.unittest_with_stats_sqlite import Unittest_with_stats_sqlite
from edcore.tests.utils.unittest_with_edcore_sqlite import (get_unittest_tenant_name, Unittest_with_edcore_sqlite,
                                                            UnittestEdcoreDBConnection)
from edextract.data_extract_generation.item_level_generator import generate_items_csv, _get_path_to_item_csv, \
    _append_csv_files
from edextract.status.constants import Constants
from edextract.tasks.constants import Constants as TaskConstants, QueryType


class TestItemLevelGenerator(Unittest_with_stats_sqlite, Unittest_with_edcore_sqlite):
    __tmp_item_dir = tempfile.mkdtemp('item_level_files')
    __built_files = False

    def setUp(self):
        self.__tmp_out_dir = tempfile.mkdtemp('item_file_archiver_test')
        self._tenant = get_unittest_tenant_name()
        self.__state_code = 'NC'
        set_tenant_map({get_unittest_tenant_name(): 'NC'})
        if not TestItemLevelGenerator.__built_files:
            self.__build_item_level_files()
            TestItemLevelGenerator.__built_files = True

    def tearDown(self):
        shutil.rmtree(self.__tmp_out_dir)
        pass

    @classmethod
    def setUpClass(cls):
        Unittest_with_edcore_sqlite.setUpClass()
        Unittest_with_stats_sqlite.setUpClass()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TestItemLevelGenerator.__tmp_item_dir)
        Unittest_with_edcore_sqlite.tearDownClass()
        # Unittest_with_stats_sqlite.tearDownClass()  # Not sure why we don't need to do this

    def test_generate_item_csv_success_no_item_ids(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'asmtGrade': '3'}
        query = self.__create_query(params)
        print(query)
        output = os.path.join(self.__tmp_out_dir, 'items.csv')
        task_info = {Constants.TASK_ID: '01',
                     Constants.CELERY_TASK_ID: '02',
                     Constants.REQUEST_GUID: '03'}
        extract_args = {TaskConstants.TASK_QUERIES: {QueryType.QUERY: query},
                        TaskConstants.ROOT_DIRECTORY: self.__tmp_item_dir,
                        TaskConstants.ITEM_IDS: None}
        generate_items_csv(self._tenant, output, task_info, extract_args)
        self.assertTrue(os.path.exists(output))
        csv_data = []
        with open(output) as out:
            data = csv.reader(out)
            for row in data:
                csv_data.append(row)
        self.assertEqual(len(csv_data), 211)
        self.assertIn('key', csv_data[0])
        self.assertIn('student_guid', csv_data[0])
        self.assertIn('score', csv_data[0])

    def test_generate_item_csv_success_item_ids(self):
        params = {'stateCode': 'NC',
                  'asmtYear': '2015',
                  'asmtType': 'SUMMATIVE',
                  'asmtSubject': 'Math',
                  'asmtGrade': '3'}
        query = self.__create_query(params)
        output = os.path.join(self.__tmp_out_dir, 'items.csv')
        task_info = {Constants.TASK_ID: '01',
                     Constants.CELERY_TASK_ID: '02',
                     Constants.REQUEST_GUID: '03'}
        extract_args = {TaskConstants.TASK_QUERIES: {QueryType.QUERY: query},
                        TaskConstants.ROOT_DIRECTORY: self.__tmp_item_dir,
                        TaskConstants.ITEM_IDS: ['160', '150']}
        generate_items_csv(self._tenant, output, task_info, extract_args)
        self.assertTrue(os.path.exists(output))
        csv_data = []
        with open(output) as out:
            data = csv.reader(out)
            for row in data:
                csv_data.append(row)
        self.assertEqual(len(csv_data), 66)
        self.assertIn('key', csv_data[0])
        self.assertIn('student_guid', csv_data[0])
        self.assertIn('score', csv_data[0])

    def test_get_path_to_item_csv(self):
        items_root_dir = os.path.dirname(os.path.abspath(__file__))
        record = {}
        path = _get_path_to_item_csv(items_root_dir, **record)
        self.assertEqual(path, items_root_dir)

        record = {'state_code': 'NC'}
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(items_root_dir, 'NC')
        self.assertEqual(path, expect_path)

        record['asmt_year'] = 2015
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(expect_path, '2015')
        self.assertEqual(path, expect_path)

        record['asmt_type'] = 'SUMMATIVE'
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(expect_path, 'SUMMATIVE')
        self.assertEqual(path, expect_path)

        record['effective_date'] = 20150402
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(expect_path, '20150402')
        self.assertEqual(path, expect_path)

        record['asmt_subject'] = 'Math'
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(expect_path, 'MATH')
        self.assertEqual(path, expect_path)

        record['asmt_grade'] = 3
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(expect_path, '3')
        self.assertEqual(path, expect_path)

        record['district_guid'] = '3ab54de78a'
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(expect_path, '3ab54de78a')
        self.assertEqual(path, expect_path)

        record['student_guid'] = 'a78dbf34'
        path = _get_path_to_item_csv(items_root_dir, **record)
        expect_path = os.path.join(expect_path, 'a78dbf34.csv')
        self.assertEqual(path, expect_path)

    def test_append_csv_files(self):
        record = {'state_code': 'NC',
                  'asmt_year': 2015,
                  'asmt_type': 'INTERIM COMPREHENSIVE',
                  'effective_date': 20150106,
                  'asmt_subject': 'ELA',
                  'asmt_grade': 3,
                  'district_guid': '3ab54de78a',
                  'student_guid': 'a78dbf34'}
        tempdir = tempfile.TemporaryDirectory()
        record1 = copy.deepcopy(record)
        record1['student_guid'] = '1'
        file1 = _get_path_to_item_csv(tempdir.name, **record1)
        record2 = copy.deepcopy(record)
        record2['student_guid'] = '2'
        file2 = _get_path_to_item_csv(tempdir.name, **record2)
        record3 = copy.deepcopy(record)
        record3['student_guid'] = '3'
        file3 = _get_path_to_item_csv(tempdir.name, **record3)
        os.makedirs(os.path.dirname(file1))
        with open(file1, 'w') as csv1:
            csvwriter1 = csv.writer(csv1, delimiter=',')
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome1'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome2'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome3'])
        with open(file2, 'w') as csv1:
            csvwriter1 = csv.writer(csv1, delimiter=',')
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome1'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome2'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome3'])
        with open(file3, 'w') as csv1:
            csvwriter1 = csv.writer(csv1, delimiter=',')
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome1'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome2'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome3'])
        results = [record1, record2, record3]
        outputfile = os.path.join(tempdir.name, 'output')
        csv_header = ['abc', 'efg', 'xes']
        _append_csv_files(tempdir.name, None, results, outputfile, csv_header)
        self.assertTrue(os.path.isfile(outputfile))
        with open(outputfile, 'r') as file:
            csvfile = csv.reader(file, delimiter=',')
            header = next(csvfile)
            self.assertEqual(header, csv_header)
            count_row = 0
            for _ in csvfile:
                count_row += 1
            self.assertEqual(9, count_row)
        tempdir.cleanup()

    def test_append_csv_files_multiple_output(self):
        record = {'state_code': 'NC',
                  'asmt_year': 2015,
                  'asmt_type': 'INTERIM COMPREHENSIVE',
                  'effective_date': 20150106,
                  'asmt_subject': 'ELA',
                  'asmt_grade': 3,
                  'district_guid': '3ab54de78a',
                  'student_guid': 'a78dbf34'}
        tempdir = tempfile.TemporaryDirectory()
        record1 = copy.deepcopy(record)
        record1['student_guid'] = '1'
        file1 = _get_path_to_item_csv(tempdir.name, **record1)
        record2 = copy.deepcopy(record)
        record2['student_guid'] = '2'
        file2 = _get_path_to_item_csv(tempdir.name, **record2)
        record3 = copy.deepcopy(record)
        record3['student_guid'] = '3'
        file3 = _get_path_to_item_csv(tempdir.name, **record3)
        os.makedirs(os.path.dirname(file1))
        with open(file1, 'w') as csv1:
            csvwriter1 = csv.writer(csv1, delimiter=',')
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome1'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome2'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome3'])
        with open(file2, 'w') as csv1:
            csvwriter1 = csv.writer(csv1, delimiter=',')
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome1'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome2'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome3'])
        with open(file3, 'w') as csv1:
            csvwriter1 = csv.writer(csv1, delimiter=',')
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome1'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome2'])
            csvwriter1.writerow(['hello', 'world', 'you', 'are', 'awesome3'])
        results = [record1, record2, record3]
        outputfile1 = os.path.join(tempdir.name, 'output1')
        outputfile2 = os.path.join(tempdir.name, 'output2')
        outputfiles = [outputfile1, outputfile2]
        csv_header = ['abc', 'efg', 'xes']
        _append_csv_files(tempdir.name, None, results, outputfiles, csv_header)
        self.assertTrue(os.path.isfile(outputfile1))
        self.assertTrue(os.path.isfile(outputfile2))
        with open(outputfile1, 'r') as file:
            csvfile = csv.reader(file, delimiter=',')
            header = next(csvfile)
            self.assertEqual(header, csv_header)
            count_row = 0
            for _ in csvfile:
                count_row += 1
            self.assertEqual(3, count_row)
        with open(outputfile2, 'r') as file:
            csvfile = csv.reader(file, delimiter=',')
            header = next(csvfile)
            self.assertEqual(header, csv_header)
            count_row = 0
            for _ in csvfile:
                count_row += 1
            self.assertEqual(6, count_row)
        tempdir.cleanup()

    def __create_query(self, params):
        with UnittestEdcoreDBConnection() as connection:
            dim_asmt = connection.get_table('dim_asmt')
            fact_asmt_outcome_vw = connection.get_table('fact_asmt_outcome_vw')
            query = select([fact_asmt_outcome_vw.c.state_code,
                            fact_asmt_outcome_vw.c.asmt_year,
                            fact_asmt_outcome_vw.c.asmt_type,
                            dim_asmt.c.effective_date,
                            fact_asmt_outcome_vw.c.asmt_subject,
                            fact_asmt_outcome_vw.c.asmt_grade,
                            fact_asmt_outcome_vw.c.district_guid,
                            fact_asmt_outcome_vw.c.student_guid],
                           from_obj=[fact_asmt_outcome_vw
                                     .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id))])

            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_year == params['asmtYear']))
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_type == params['asmtType']))
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_subject == params['asmtSubject']))
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_grade == params['asmtGrade']))
            query = query.where(and_(fact_asmt_outcome_vw.c.rec_status == 'C'))
            return query

    def __build_item_pool(self, asmt_count):
        pool = []
        for i in range(10):
            pool.append({'key': i + (asmt_count * 10), 'client': i + (asmt_count * 10),
                         'type': 'MC', 'segment': 'segment_name_ut'})
        return pool

    def __build_item_level_files(self):
        with UnittestEdcoreDBConnection() as connection:
            item_pools, asmt_count, flip_flop = {}, 0, False
            fact_asmt = connection.get_table('fact_asmt_outcome_vw')
            dim_asmt = connection.get_table('dim_asmt')
            query = select([fact_asmt.c.state_code, fact_asmt.c.asmt_year, fact_asmt.c.asmt_type,
                            dim_asmt.c.effective_date, fact_asmt.c.asmt_subject, fact_asmt.c.asmt_grade,
                            fact_asmt.c.district_guid, fact_asmt.c.student_guid, fact_asmt.c.asmt_guid],
                           from_obj=[fact_asmt
                                     .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt.c.asmt_rec_id))])
            query = query.where(fact_asmt.c.rec_status == 'C')
            query = query.order_by(fact_asmt.c.asmt_guid, fact_asmt.c.student_guid)
            results = connection.get_result(query)
            for result in results:
                asmt_guid = result['asmt_guid']
                if asmt_guid not in item_pools:
                    item_pools[asmt_guid] = self.__build_item_pool(asmt_count)
                    asmt_count += 1
                    flip_flop = False

                if flip_flop:
                    student_pool = item_pools[asmt_guid][0:5]
                else:
                    student_pool = item_pools[asmt_guid][5:10]
                flip_flop = not flip_flop

                dir_path = os.path.join(TestItemLevelGenerator.__tmp_item_dir, str(result['state_code']).upper(),
                                        str(result['asmt_year']), str(result['asmt_type']).upper().replace(' ', '_'),
                                        str(result['effective_date']), str(result['asmt_subject']).upper(),
                                        str(result['asmt_grade']), str(result['district_guid']))
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                with open(_get_path_to_item_csv(TestItemLevelGenerator.__tmp_item_dir, **dict(result)), 'w') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    for item in student_pool:
                        csv_writer.writerow([item['key'], result['student_guid'], item['segment'], 0, item['client'],
                                             1, 1, item['type'], 0, 1, '2013-04-03T16:21:33.660', 1, 'MA-Undesignated',
                                             'MA-Undesignated', 1, 1, 1, 0])
import copy
