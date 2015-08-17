'''
Created on Aug 12, 2014

@author: dip
'''
import unittest
from smarter_score_batcher.processing.assessment import XMLMeta, Mapping,\
    get_assessment_mapping, AssessmentHeaders, AssessmentData,\
    getClaimMappingName, get_groups, get_accommodations, get_claims
from smarter_score_batcher.tests.processing.utils import DummyObj, read_data
import os
import json
from smarter_score_batcher.utils.constants import PerformanceMetadataConstants
from smarter_score_batcher.error.exceptions import MetadataException
import hashlib


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
        self.assertEquals(val, 1)

    def test_get_csv_mapping(self):
        here = os.path.abspath(os.path.dirname(__file__))
        static_metadata = os.path.join(here, '..', 'resources', 'meta', 'static', 'ELA.static_asmt_metadata.json')
        metadata = self.load_metadata(static_metadata)
        data = read_data("assessment.xml")
        root = ET.fromstring(data)
        state_code, data = get_assessment_mapping(root, metadata)
        header = data.header
        values = data.values
        self.assertEqual(len(header), len(values))
        self.assertTrue(len(header) > 0)
        mapping = dict(zip(header, values))
        self.assertEqual(mapping[AssessmentHeaders.AssessmentGuid], 'SBAC-FT-SomeDescription-ELA-7')
        self.assertEqual(mapping[AssessmentHeaders.AccommodationBraille], '6')
        self.assertEqual(mapping[AssessmentHeaders.StudentIdentifier], '77043c80-4b0a-11e4-916c-0800200c9a66')
        self.assertEqual(mapping[AssessmentHeaders.Asian], 'No')
        self.assertEqual(mapping[AssessmentHeaders.ResponsibleSchoolIdentifier], 'CA_9999827_9999928')
        self.assertEqual(mapping[AssessmentHeaders.NameOfInstitution], 'My Elementary School')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSessionLocationId], '1855629')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSessionLocation], '562299-SBASQL8')
        self.assertEqual(mapping[AssessmentHeaders.AccommodationAmericanSignLanguage], '6')
        self.assertEqual(mapping[AssessmentHeaders.Birthdate], '20130831')
        self.assertEqual(mapping[AssessmentHeaders.StateAbbreviation], 'CA')
        self.assertEqual(mapping[AssessmentHeaders.ResponsibleDistrictIdentifier], 'CA_9999827')
        self.assertEqual(mapping[AssessmentHeaders.OrganizationName], 'This Elementary School District')
        self.assertEqual(mapping[AssessmentHeaders.ExternalSSID], 'CA-9999999598')
        self.assertEqual(mapping[AssessmentHeaders.FirstName], 'John')
        self.assertEqual(mapping[AssessmentHeaders.LastOrSurname], 'Smith')
        self.assertEqual(mapping[AssessmentHeaders.Sex], 'Male')
        self.assertEqual(mapping[AssessmentHeaders.GradeLevelWhenAssessed], '3')
        self.assertEqual(mapping[AssessmentHeaders.HispanicOrLatinoEthnicity], 'No')
        self.assertEqual(mapping[AssessmentHeaders.AmericanIndianOrAlaskaNative], 'No')
        self.assertEqual(mapping[AssessmentHeaders.Asian], 'No')
        self.assertEqual(mapping[AssessmentHeaders.BlackOrAfricanAmerican], 'Yes')
        self.assertEqual(mapping[AssessmentHeaders.NativeHawaiianOrOtherPacificIslander], 'No')
        self.assertEqual(mapping[AssessmentHeaders.White], 'No')
        self.assertEqual(mapping[AssessmentHeaders.DemographicRaceTwoOrMoreRaces], 'No')
        self.assertEqual(mapping[AssessmentHeaders.IDEAIndicator], 'No')
        self.assertEqual(mapping[AssessmentHeaders.LEPStatus], 'Yes')
        self.assertEqual(mapping[AssessmentHeaders.Section504Status], 'No')
        self.assertEqual(mapping[AssessmentHeaders.EconomicDisadvantageStatus], 'No')
        self.assertEqual(mapping[AssessmentHeaders.MigrantStatus], 'Yes')
        # test groups
        self.assertEqual(mapping[AssessmentHeaders.Group1Id], hashlib.sha1('Brennan Math'.encode()).hexdigest())
        self.assertEqual(mapping[AssessmentHeaders.Group1Text], 'Brennan Math')
        self.assertEqual(mapping[AssessmentHeaders.Group2Id], hashlib.sha1('Tuesday Science'.encode()).hexdigest())
        self.assertEqual(mapping[AssessmentHeaders.Group2Text], 'Tuesday Science')
        self.assertEqual(mapping[AssessmentHeaders.Group3Id], hashlib.sha1('Smith Research'.encode()).hexdigest())
        self.assertEqual(mapping[AssessmentHeaders.Group3Text], 'Smith Research')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentAdministrationFinishDate], '20140414')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentYear], '2014')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentType], 'SUMMATIVE')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentLevelForWhichDesigned], '3')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestResultScoreValue], '245.174914080214')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestMinimumValue], '226')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestMaximumValue], '264')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentPerformanceLevelIdentifier], '2')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestResultScoreClaim1Value], '352.897')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim1MinimumValue], '-267')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim1MaximumValue], '971')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentClaim1PerformanceLevelIdentifier], '2')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestResultScoreClaim2Value], '185.002')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim2MinimumValue], '107')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim2MaximumValue], '263')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentClaim2PerformanceLevelIdentifier], '1')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestResultScoreClaim3Value], '403.416')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim3MinimumValue], '199')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim3MaximumValue], '607')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentClaim3PerformanceLevelIdentifier], '2')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestResultScoreClaim4Value], '403.416')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim4MinimumValue], '199')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentSubtestClaim4MaximumValue], '607')
        self.assertEqual(mapping[AssessmentHeaders.AssessmentClaim4PerformanceLevelIdentifier], '2')

    def test_assessment_data_class(self):
        data = AssessmentData([Mapping(DummyObj(), "test_header")])
        data.evaluate()
        self.assertListEqual(data.header, ['test_header'])
        self.assertListEqual(data.values, [1])

    def test_getClaimMappingName(self):
        here = os.path.abspath(os.path.dirname(__file__))
        static_metadata = os.path.join(here, '..', 'resources', 'meta', 'static', 'MATH.static_asmt_metadata.json')
        metadata = self.load_metadata(static_metadata)
        mapping = getClaimMappingName(metadata, 'hello', 'world')
        self.assertEqual(mapping, 'world')
        mapping = getClaimMappingName(metadata, PerformanceMetadataConstants.CLAIM2, 'world')
        self.assertEqual(mapping, 'Claim2Problem Solving and Modeling & Data Analysis')
        mapping = getClaimMappingName(None, PerformanceMetadataConstants.CLAIM2, 'world')
        self.assertEqual(mapping, 'world')

    def test_get_groups(self):
        data = read_data("assessment.xml")
        examinee = ET.fromstring(data).find("./Examinee")
        group_mappings = get_groups(examinee)
        self.assertEqual(len(group_mappings), 20)
        self.assertEqual(group_mappings[0].evaluate(), 'afa6289f535474b99d6dac29e3a2b8782b0fe0b7')
        self.assertEqual(group_mappings[1].evaluate(), 'Brennan Math')
        self.assertEqual(group_mappings[2].evaluate(), '5b62bc83fb94dc4d1961c00f8c93809b57c56dc9')
        self.assertEqual(group_mappings[3].evaluate(), 'Tuesday Science')
        self.assertEqual(group_mappings[4].evaluate(), '6697b20b4902b5812f1221c2746600b476f61a20')
        self.assertEqual(group_mappings[5].evaluate(), 'Smith Research')
        self.assertEqual(group_mappings[6].evaluate(), '')
        self.assertEqual(group_mappings[7].evaluate(), '')

    def test_get_accommodations(self):
        data = read_data("assessment.xml")
        opportunity = ET.fromstring(data).find("./Opportunity")
        accommodations = get_accommodations(opportunity)
        self.assertEqual(len(accommodations), 15)
        self.assertEqual(accommodations[0].evaluate(), '6')
        self.assertEqual(accommodations[1].evaluate(), '6')
        self.assertEqual(accommodations[2].evaluate(), '6')
        self.assertEqual(accommodations[3].evaluate(), '4')
        self.assertEqual(accommodations[4].evaluate(), '4')
        self.assertEqual(accommodations[5].evaluate(), '0')
        self.assertEqual(accommodations[6].evaluate(), '6')
        self.assertEqual(accommodations[7].evaluate(), '6')
        self.assertEqual(accommodations[8].evaluate(), '6')
        self.assertEqual(accommodations[9].evaluate(), '6')
        self.assertEqual(accommodations[10].evaluate(), '0')
        self.assertEqual(accommodations[11].evaluate(), '0')
        self.assertEqual(accommodations[12].evaluate(), '0')
        self.assertEqual(accommodations[13].evaluate(), '0')
        self.assertEqual(accommodations[14].evaluate(), '0')

    def test_iab_get_claims(self):
        data = read_data("iab_assessment.xml")
        opportunity = ET.fromstring(data).find("./Opportunity")
        here = os.path.abspath(os.path.dirname(__file__))
        static_metadata = os.path.join(here, '..', 'resources', 'meta', 'default', 'interim assessment blocks', 'MATH.default_asmt_metadata.json')
        # read metadata and map Claim1, Claim2, Claim3, and Claim4
        metadata = self.load_metadata(static_metadata)
        claims = get_claims(metadata, opportunity)
        self.assertEqual(len(claims), 20)

        # overall
        self.assertEqual(claims[0].evaluate(), None)
        self.assertEqual(claims[1].evaluate(), None)
        self.assertEqual(claims[2].evaluate(), '0')
        self.assertEqual(claims[3].evaluate(), '0')
        # all claims should be empty except claim1
        # claim1
        self.assertEqual(claims[4].evaluate(), None)
        self.assertEqual(claims[5].evaluate(), '0')
        self.assertEqual(claims[6].evaluate(), '0')
        self.assertEqual(claims[7].evaluate(), None)
        # claim2
        self.assertEqual(claims[8].evaluate(), None)
        self.assertEqual(claims[9].evaluate(), '0')
        self.assertEqual(claims[10].evaluate(), '0')
        self.assertEqual(claims[11].evaluate(), None)
        # claim3
        self.assertEqual(claims[12].evaluate(), None)
        self.assertEqual(claims[13].evaluate(), '0')
        self.assertEqual(claims[14].evaluate(), '0')
        self.assertEqual(claims[15].evaluate(), None)
        # claim4
        self.assertEqual(claims[16].evaluate(), None)
        self.assertEqual(claims[17].evaluate(), '0')
        self.assertEqual(claims[18].evaluate(), '0')
        self.assertEqual(claims[19].evaluate(), None)

    def load_metadata(self, metadata_file_path):
        # read metadata and map Claim1, Claim2, Claim3, and Claim4
        metadata = None
        with open(metadata_file_path) as f:
            metadata_json = f.read()
            metadata = json.loads(metadata_json)
        return metadata


if __name__ == "__main__":
    unittest.main()
