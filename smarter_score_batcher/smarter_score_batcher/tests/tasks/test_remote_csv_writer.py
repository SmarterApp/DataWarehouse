import unittest
import tempfile
import os
import csv
from smarter_score_batcher.utils import meta
from smarter_score_batcher.utils.file_utils import file_writer, create_path
from smarter_score_batcher.tasks.remote_csv_writer import remote_csv_generator
from pyramid.registry import Registry
from pyramid import testing
from smarter_score_batcher.celery import setup_celery
import uuid
from edcore.utils.file_utils import generate_path_to_raw_xml,\
    generate_path_to_item_csv
from zope import component
from smarter_score_batcher.templates.asmt_template_manager import IMetadataTemplateManager,\
    PerfMetadataTemplateManager
from zope.component.globalregistry import base
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options


class Test(unittest.TestCase):
    def setUp(self):
        self.__tempfolder = tempfile.TemporaryDirectory()
        settings = {
            'smarter_score_batcher.celery_timeout': 30,
            'smarter_score_batcher.celery.celery_always_eager': True,
            'smarter_score_batcher.base_dir': self.__tempfolder.name
        }
        reg = Registry()
        reg.settings = settings
        reg.utilities = base.utilities
        CacheManager(**parse_cache_config_options({'cache.regions': 'public.shortlived', 'cache.type': 'memory', 'cache.public.shortlived.expire': 7200}))
        self.__config = testing.setUp(registry=reg)
        setup_celery(settings)
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../resources/meta/performance')
        static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../resources/meta/static')
        component.provideUtility(PerfMetadataTemplateManager(asmt_meta_dir=path, static_asmt_meta_dir=static_path), IMetadataTemplateManager)

    def tearDown(self):
        self.__tempfolder.cleanup()
        testing.tearDown()

    def test_create_csv(self):
        root_dir_xml = os.path.join(self.__tempfolder.name, str(uuid.uuid4()), str(uuid.uuid4()))
        root_dir_csv = os.path.join(self.__tempfolder.name, str(uuid.uuid4()), str(uuid.uuid4()))
        work_dir = os.path.join(self.__tempfolder.name, 'work_dir')
        xml_string = '''<TDSReport>
        <Test subject="MA" grade="3-12" assessmentType="Formative" academicYear="2014" />
        <Examinee key="12"></Examinee>
        <Opportunity>
        <Item position="position_value" segmentId="segmentId_value"
        bankKey="test" key="key_value" operational="operational_value" isSelected="isSelected_value" format="format_type_value"
        score="score_value" scoreStatus="scoreStatus_value" adminDate="adminDate_value" numberVisits="numberVisits_value"
        mimeType="test" strand="strand_value" contentLevel="contentLevel_value" pageNumber="pageNumber_value" pageVisits="pageVisits_value"
        pageTime="pageTime_value" dropped="dropped_value">
        </Item>
        </Opportunity>
        </TDSReport>'''
        meta_names = meta.Meta(True, '12', 'test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8', 'test9')
        xml_file_path = create_path(root_dir_xml, meta_names, generate_path_to_raw_xml)
        file_writer(xml_file_path, xml_string)
        rows = []
        csv_file_path = create_path(root_dir_csv, meta_names, generate_path_to_item_csv)
        remote_csv_generator(meta_names, csv_file_path, xml_file_path, work_dir)
        with open(csv_file_path, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rows.append(row)
        csv_first_row_list = ['key_value', '12', 'segmentId_value', 'position_value', '', 'operational_value', 'isSelected_value', 'format_type_value', 'score_value', 'scoreStatus_value', 'adminDate_value', 'numberVisits_value', 'strand_value', 'contentLevel_value', 'pageNumber_value', 'pageVisits_value', 'pageTime_value', 'dropped_value']
        self.assertEqual(1, len(rows))
        self.assertEqual(csv_first_row_list, rows[0])

if __name__ == "__main__":
    unittest.main()
