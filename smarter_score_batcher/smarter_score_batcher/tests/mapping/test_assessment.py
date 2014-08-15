'''
Created on Aug 12, 2014

@author: dip
'''
import unittest
from smarter_score_batcher.mapping.assessment import XMLMeta, Mapping,\
    get_assessment_mapping, AssessmentHeaders
from smarter_score_batcher.tests.mapping.utils import DummyObj, read_data
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class TestCSVMetadata(unittest.TestCase):

    def test_xml_metadata_with_attribute_in_node(self):
        data = '''<TDSReport>
        <Test subject="MA" grade="3-12" assessmentType="Formative" academicYear="2014" />
        </TDSReport>'''
        root = ET.fromstring(data)
        xmlmeta = XMLMeta(root, './Test', 'grade')
        val = xmlmeta.get_value()
        self.assertEquals(val, '3-12')

    def test_xml_metadata_with_attribute_to_compare(self):
        data = '''<TDSReport>
        <Accommodation type="Speech to Text" value="9" context="FINAL" />
        </TDSReport>'''
        root = ET.fromstring(data)
        xmlmeta = XMLMeta(root, "./Accommodation/[@type='Speech to Text']", 'value', 'context')
        val = xmlmeta.get_value()
        self.assertEquals(val, '9')

    def test_mapping_class(self):
        mapping = Mapping(DummyObj(), 'test')
        val = mapping.evaluate()
        self.assertEquals(val['test'], 1)

    def test_get_csv_mapping(self):
        data = read_data("assessment.xml")
        root = ET.fromstring(data)
        mapping = get_assessment_mapping(root)
        self.assertEqual(mapping[AssessmentHeaders.AssessmentGuid], 'SBAC-FT-SomeDescription-MATH-7')
        self.assertEqual(mapping[AssessmentHeaders.AccommodationBraille], '8')
        self.assertEqual(mapping[AssessmentHeaders.StudentIdentifier], '12')
        self.assertEqual(mapping[AssessmentHeaders.Asian], 'No')
        self.assertIsNone(mapping[AssessmentHeaders.Group1Id], None)
        self.assertEqual(mapping[AssessmentHeaders.NameOfInstitution], 'My Elementary School')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSessionLocationId], '1855629')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestResultScoreValue], '1295')
        self.assertEqual(mapping[AssessmentHeaders.AccommodationAmericanSignLanguage], '4')


if __name__ == "__main__":
    unittest.main()
