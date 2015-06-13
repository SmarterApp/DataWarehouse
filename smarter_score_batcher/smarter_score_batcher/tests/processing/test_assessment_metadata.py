'''
Created on Aug 12, 2014

@author: dip
'''
import unittest
from smarter_score_batcher.processing.assessment_metadata import JSONHeaders, JSONMapping,\
    get_assessment_metadata_mapping
from smarter_score_batcher.tests.processing.utils import DummyObj, read_data
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import os
from smarter_score_batcher.templates.asmt_template_manager import PerfMetadataTemplateManager,\
    IMetadataTemplateManager
from zope import component
import json
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class TestJSONMetadata(unittest.TestCase):

    def setUp(self):
        CacheManager(**parse_cache_config_options({'cache.regions': 'public.shortlived', 'cache.type': 'memory', 'cache.public.shortlived.expire': 7200}))
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../resources/meta/performance')
        static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../resources/meta/static')
        component.provideUtility(PerfMetadataTemplateManager(asmt_meta_dir=path, static_asmt_meta_dir=static_path), IMetadataTemplateManager)
        static_json = os.path.join(static_path, 'ELA.static_asmt_metadata.json')
        with open(static_json) as f:
            self.__metadata = json.loads(f.read())

    def test_JSONHeaders_obj(self):
        out = JSONHeaders(self.__metadata)
        values = out.get_values()
        self.assertIsNotNone(values)
        self.assertIsNone(values['Identification'].get('Guid'))
        out.asmt_guid = 'abc'
        self.assertEqual(values['Identification']['Guid'], 'abc')

    def test_JSONMapping(self):
        header = JSONHeaders(self.__metadata)
        mapping = JSONMapping(DummyObj().get_value(), header, 'asmt_guid')
        mapping.evaluate()
        self.assertEqual(header.asmt_guid, 1)

    def test_get_json_mapping(self):
        data = read_data("assessment.xml")
        root = ET.fromstring(data)
        asmt_guid, mapping = get_assessment_metadata_mapping(root)
        self.assertEqual(asmt_guid, 'SBAC-FT-SomeDescription-ELA-7')
        self.assertEqual(mapping['Identification']['Guid'], 'SBAC-FT-SomeDescription-ELA-7')
        self.assertEqual(mapping['Overall']['MinScore'], '1000')
        self.assertEqual(mapping['PerformanceLevels']['Level1']['Name'], 'Minimal Understanding')
        self.assertEqual(mapping['Claims']['Claim1']['MinScore'], '0')
        self.assertEqual(mapping['ClaimsPerformanceLevel']['Level2']['Name'], 'At/Near Standard')
        self.assertEqual(mapping['Identification']['EffectiveDate'], '20140414')
        self.assertEqual(mapping['Identification']['Subject'], 'ELA')

if __name__ == "__main__":
    unittest.main()
