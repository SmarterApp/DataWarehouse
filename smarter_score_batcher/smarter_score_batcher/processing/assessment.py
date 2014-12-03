'''
Created on Aug 8, 2014

@author: dip
'''
from smarter_score_batcher.utils.xml_utils import extract_meta_with_fallback_helper, \
    extract_meta_without_fallback_helper
import itertools
import json
from smarter_score_batcher.utils.constants import PerformanceMetadataConstants
from smarter_score_batcher.error.exceptions import MetadataException
from edcore.utils.utils import xml_datetime_convert
import hashlib


class XMLMeta:
    '''
    Used for storing and extracting elements from xml
    '''
    def __init__(self, root, xpath, attribute, attribute_to_compare=None):
        self.root = root
        self.path = xpath
        self.attribute = attribute
        self.attribute_to_compare = attribute_to_compare

    def get_value(self):
        if self.attribute_to_compare:
            val = extract_meta_with_fallback_helper(self.root, self.path, self.attribute, self.attribute_to_compare)
        else:
            val = extract_meta_without_fallback_helper(self.root, self.path, self.attribute)
        return val


class DateMeta(XMLMeta):

    def get_value(self):
        date = super().get_value()
        return xml_datetime_convert(date)


class IntegerMeta(XMLMeta):

    def get_value(self):
        data = super().get_value()
        return str(int(data)) if data else data


class HashMeta(XMLMeta):
    '''
    Evaluates the value from XML attribute, and hashes it
    '''

    def get_value(self):
        data = super().get_value()
        return hashlib.sha1(data.encode("utf-8")).hexdigest()


class ValueMeta():

    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value


class XMLClaimScore:
    '''
    Accommodation Specific - Perhaps to handle default values
    '''
    def __init__(self, root, xpath, scaleScore_attribute, standardError_attribute):
        self.__scaleScore = XMLMeta(root, xpath, scaleScore_attribute)
        self.__standardError = XMLMeta(root, xpath, standardError_attribute)
        self.__value_scaleScore = self.__scaleScore.get_value()
        self.__value_standardError = self.__standardError.get_value()

    def get_max(self):
        meta = XMLClaimScore.XMLClaimScoreMeta(str(int(float(self.__value_scaleScore if self.__value_scaleScore is not None else 0)) + int(float(self.__value_standardError if self.__value_standardError is not None else 0))))
        return meta

    def get_min(self):
        meta = XMLClaimScore.XMLClaimScoreMeta(str(int(float(self.__value_scaleScore if self.__value_scaleScore is not None else 0)) - int(float(self.__value_standardError if self.__value_standardError is not None else 0))))
        return meta

    class XMLClaimScoreMeta():
        def __init__(self, value):
            self.__value = value

        def get_value(self):
            return self.__value


class Mapping:
    '''
    Used for storing and evaluating mapping from xml to csv
    '''
    def __init__(self, src, target):
        self.src = src
        self.target = target

    def evaluate(self):
        return self.src.get_value()


class AssessmentHeaders:
    '''
    Constants for assessment csv landing zone file
    '''
    # In the order of csv headers
    StateAbbreviation = 'StateAbbreviation'
    ResponsibleDistrictIdentifier = 'ResponsibleDistrictIdentifier'
    OrganizationName = 'OrganizationName'
    ResponsibleSchoolIdentifier = 'ResponsibleSchoolIdentifier'
    NameOfInstitution = 'NameOfInstitution'
    StudentIdentifier = 'StudentIdentifier'
    ExternalSSID = 'ExternalSSID'
    FirstName = 'FirstName'
    MiddleName = 'MiddleName'
    LastOrSurname = 'LastOrSurname'
    Sex = 'Sex'
    Birthdate = 'Birthdate'
    GradeLevelWhenAssessed = 'GradeLevelWhenAssessed'
    HispanicOrLatinoEthnicity = 'HispanicOrLatinoEthnicity'
    AmericanIndianOrAlaskaNative = 'AmericanIndianOrAlaskaNative'
    Asian = 'Asian'
    BlackOrAfricanAmerican = 'BlackOrAfricanAmerican'
    NativeHawaiianOrOtherPacificIslander = 'NativeHawaiianOrOtherPacificIslander'
    White = 'White'
    DemographicRaceTwoOrMoreRaces = 'DemographicRaceTwoOrMoreRaces'
    IDEAIndicator = 'IDEAIndicator'
    LEPStatus = 'LEPStatus'
    Section504Status = 'Section504Status'
    EconomicDisadvantageStatus = 'EconomicDisadvantageStatus'
    MigrantStatus = 'MigrantStatus'
    Group1Id = 'Group1Id'
    Group1Text = 'Group1Text'
    Group2Id = 'Group2Id'
    Group2Text = 'Group2Text'
    Group3Id = 'Group3Id'
    Group3Text = 'Group3Text'
    Group4Id = 'Group4Id'
    Group4Text = 'Group4Text'
    Group5Id = 'Group5Id'
    Group5Text = 'Group5Text'
    Group6Id = 'Group6Id'
    Group6Text = 'Group6Text'
    Group7Id = 'Group7Id'
    Group7Text = 'Group7Text'
    Group8Id = 'Group8Id'
    Group8Text = 'Group8Text'
    Group9Id = 'Group9Id'
    Group9Text = 'Group9Text'
    Group10Id = 'Group10Id'
    Group10Text = 'Group10Text'
    AssessmentGuid = 'AssessmentGuid'
    AssessmentSessionLocationId = 'AssessmentSessionLocationId'
    AssessmentSessionLocation = 'AssessmentSessionLocation'
    AssessmentAdministrationFinishDate = 'AssessmentAdministrationFinishDate'
    AssessmentYear = 'AssessmentYear'
    AssessmentType = 'AssessmentType'
    AssessmentAcademicSubject = 'AssessmentAcademicSubject'
    AssessmentLevelForWhichDesigned = 'AssessmentLevelForWhichDesigned'
    AssessmentSubtestResultScoreValue = 'AssessmentSubtestResultScoreValue'
    AssessmentSubtestMinimumValue = 'AssessmentSubtestMinimumValue'
    AssessmentSubtestMaximumValue = 'AssessmentSubtestMaximumValue'
    AssessmentPerformanceLevelIdentifier = 'AssessmentPerformanceLevelIdentifier'
    AssessmentSubtestResultScoreClaim1Value = 'AssessmentSubtestResultScoreClaim1Value'
    AssessmentSubtestClaim1MinimumValue = 'AssessmentSubtestClaim1MinimumValue'
    AssessmentSubtestClaim1MaximumValue = 'AssessmentSubtestClaim1MaximumValue'
    AssessmentClaim1PerformanceLevelIdentifier = 'AssessmentClaim1PerformanceLevelIdentifier'
    AssessmentSubtestResultScoreClaim2Value = 'AssessmentSubtestResultScoreClaim2Value'
    AssessmentSubtestClaim2MinimumValue = 'AssessmentSubtestClaim2MinimumValue'
    AssessmentSubtestClaim2MaximumValue = 'AssessmentSubtestClaim2MaximumValue'
    AssessmentClaim2PerformanceLevelIdentifier = 'AssessmentClaim2PerformanceLevelIdentifier'
    AssessmentSubtestResultScoreClaim3Value = 'AssessmentSubtestResultScoreClaim3Value'
    AssessmentSubtestClaim3MinimumValue = 'AssessmentSubtestClaim3MinimumValue'
    AssessmentSubtestClaim3MaximumValue = 'AssessmentSubtestClaim3MaximumValue'
    AssessmentClaim3PerformanceLevelIdentifier = 'AssessmentClaim3PerformanceLevelIdentifier'
    AssessmentSubtestResultScoreClaim4Value = 'AssessmentSubtestResultScoreClaim4Value'
    AssessmentSubtestClaim4MinimumValue = 'AssessmentSubtestClaim4MinimumValue'
    AssessmentSubtestClaim4MaximumValue = 'AssessmentSubtestClaim4MaximumValue'
    AssessmentClaim4PerformanceLevelIdentifier = 'AssessmentClaim4PerformanceLevelIdentifier'
    AccommodationAmericanSignLanguage = 'AccommodationAmericanSignLanguage'
    AccommodationBraille = 'AccommodationBraille'
    AccommodationClosedCaptioning = 'AccommodationClosedCaptioning'
    AccommodationTextToSpeech = 'AccommodationTextToSpeech'
    AccommodationAbacus = 'AccommodationAbacus'
    AccommodationAlternateResponseOptions = 'AccommodationAlternateResponseOptions'
    AccommodationCalculator = 'AccommodationCalculator'
    AccommodationMultiplicationTable = 'AccommodationMultiplicationTable'
    AccommodationPrintOnDemand = 'AccommodationPrintOnDemand'
    AccommodationPrintOnDemandItems = 'AccommodationPrintOnDemandItems'
    AccommodationReadAloud = 'AccommodationReadAloud'
    AccommodationScribe = 'AccommodationScribe'
    AccommodationSpeechToText = 'AccommodationSpeechToText'
    AccommodationStreamlineMode = 'AccommodationStreamlineMode'
    AccommodationNoiseBuffer = 'AccommodationNoiseBuffer'


class AssessmentData:
    def __init__(self, *mappings):
        self.__mappings = itertools.chain(*mappings)
        self.__header = []
        self.__values = []

    def add(self, header, value):
        self.__header.append(header)
        self.__values.append(value)

    @property
    def header(self):
        return self.__header

    @property
    def values(self):
        return self.__values

    def evaluate(self):
        for m in self.__mappings:
            # Save the CSV Header, and Value Extracted from XML
            self.add(m.target, m.evaluate())


def getClaimMappingName(metadata, claim_name, default_value):
    '''
    get mapping name for claims
    '''
    mapping = default_value
    if metadata is not None:
        claims = metadata.get(PerformanceMetadataConstants.CLAIMS)
        if claims is not None:
            claim = claims.get(claim_name)
            if claim is not None:
                mapping = claim.get(PerformanceMetadataConstants.MAPPING, default_value)
    return mapping


def get_assessment_mapping(root, metadata_file_path):
    '''
    Returns the landing zone format of assessment csv file
    '''
    examinee = root.find("./Examinee")
    opportunity = root.find("./Opportunity")
    test_node = root.find("./Test")

    groups = get_groups(examinee)
    accommodations = get_accommodations(opportunity)
    claims = get_claims(metadata_file_path, opportunity)

    # In the order of the LZ mapping for easier maintenance
    mappings = AssessmentData([Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='StateAbbreviation']", "value", "context"), AssessmentHeaders.StateAbbreviation),
                               Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='DistrictID']", "value", "context"), AssessmentHeaders.ResponsibleDistrictIdentifier),
                               Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='DistrictName']", "value", "context"), AssessmentHeaders.OrganizationName),
                               Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='SchoolID']", "value", "context"), AssessmentHeaders.ResponsibleSchoolIdentifier),
                               Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='SchoolName']", "value", "context"), AssessmentHeaders.NameOfInstitution),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='StudentIdentifier']", "value", "context"), AssessmentHeaders.StudentIdentifier),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='AlternateSSID']", "value", "context"), AssessmentHeaders.ExternalSSID),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='FirstName']", "value", "context"), AssessmentHeaders.FirstName),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='MiddleName']", "value", "context"), AssessmentHeaders.MiddleName),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='LastOrSurname']", "value", "context"), AssessmentHeaders.LastOrSurname),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Sex']", "value", "context"), AssessmentHeaders.Sex),
                               Mapping(DateMeta(examinee, "./ExamineeAttribute/[@name='Birthdate']", "value", "context"), AssessmentHeaders.Birthdate),
                               Mapping(IntegerMeta(examinee, "./ExamineeAttribute/[@name='GradeLevelWhenAssessed']", "value", "context"), AssessmentHeaders.GradeLevelWhenAssessed),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='HispanicOrLatinoEthnicity']", "value", "context"), AssessmentHeaders.HispanicOrLatinoEthnicity),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='AmericanIndianOrAlaskaNative']", "value", "context"), AssessmentHeaders.AmericanIndianOrAlaskaNative),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Asian']", "value", "context"), AssessmentHeaders.Asian),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='BlackOrAfricanAmerican']", "value", "context"), AssessmentHeaders.BlackOrAfricanAmerican),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='NativeHawaiianOrOtherPacificIslander']", "value", "context"), AssessmentHeaders.NativeHawaiianOrOtherPacificIslander),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='White']", "value", "context"), AssessmentHeaders.White),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='DemographicRaceTwoOrMoreRaces']", "value", "context"), AssessmentHeaders.DemographicRaceTwoOrMoreRaces),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='IDEAIndicator']", "value", "context"), AssessmentHeaders.IDEAIndicator),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='LEPStatus']", "value", "context"), AssessmentHeaders.LEPStatus),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Section504Status']", "value", "context"), AssessmentHeaders.Section504Status),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='EconomicDisadvantageStatus']", "value", "context"), AssessmentHeaders.EconomicDisadvantageStatus),
                               Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='MigrantStatus']", "value", "context"), AssessmentHeaders.MigrantStatus),

                               Mapping(XMLMeta(test_node, ".", "testId"), AssessmentHeaders.AssessmentGuid),
                               Mapping(XMLMeta(opportunity, ".", "oppId"), AssessmentHeaders.AssessmentSessionLocationId),
                               Mapping(XMLMeta(opportunity, ".", "server"), AssessmentHeaders.AssessmentSessionLocation),
                               Mapping(DateMeta(opportunity, ".", "dateCompleted"), AssessmentHeaders.AssessmentAdministrationFinishDate),
                               Mapping(XMLMeta(test_node, ".", "academicYear"), AssessmentHeaders.AssessmentYear),
                               Mapping(XMLMeta(test_node, ".", "assessmentType"), AssessmentHeaders.AssessmentType),
                               Mapping(XMLMeta(test_node, ".", "subject"), AssessmentHeaders.AssessmentAcademicSubject),
                               Mapping(IntegerMeta(test_node, ".", "grade"), AssessmentHeaders.AssessmentLevelForWhichDesigned)],
                              claims, groups, accommodations)
    mappings.evaluate()
    return mappings


def get_groups(examinee):
    '''
    Get groupings from XML <ExamineeRelationship> elements.
    Assign element of list of group to group1, group2, .., group10 according to its order in the list

    map element with attribute 'StudentGroupName' to groups based on their order displaying in XML
    only display first 10 groups
    '''
    TOTAL_GROUPS = 10
    mappings = []
    groups = examinee.findall("./ExamineeRelationship[@name='StudentGroupName']")[:TOTAL_GROUPS]
    for i in range(TOTAL_GROUPS):
        if i < len(groups):
            meta = XMLMeta(groups[i], '.', 'value')
            group_id = HashMeta(groups[i], '.', 'value')
        else:
            meta = ValueMeta('')
            group_id = ValueMeta('')

        mappings.append(Mapping(group_id, 'Group%dId' % (i + 1)))
        mappings.append(Mapping(meta, 'Group%dText' % (i + 1)))
    return mappings


ACCOMMODATION_CONFIGS = [
    {'type': 'AmericanSignLanguage', 'target': AssessmentHeaders.AccommodationAmericanSignLanguage},
    {'type': 'ClosedCaptioning', 'target': AssessmentHeaders.AccommodationClosedCaptioning},
    {'type': 'Language', 'target': AssessmentHeaders.AccommodationBraille},
    {'type': 'TextToSpeech', 'target': AssessmentHeaders.AccommodationTextToSpeech},
    {'type': 'StreamlinedInterface', 'target': AssessmentHeaders.AccommodationStreamlineMode},
    {'type': 'PrintOnDemand', 'code': 'TDS_PoD0', 'target': AssessmentHeaders.AccommodationPrintOnDemand},
    {'type': 'PrintOnDemand', 'code': 'TDS_PoD_Stim&TDS_PoD_Item', 'target': AssessmentHeaders.AccommodationPrintOnDemandItems},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_Abacus', 'target': AssessmentHeaders.AccommodationAbacus},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_AR', 'target': AssessmentHeaders.AccommodationAlternateResponseOptions},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_RA_Stimuli', 'target': AssessmentHeaders.AccommodationReadAloud},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_Calc', 'target': AssessmentHeaders.AccommodationCalculator},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_MT', 'target': AssessmentHeaders.AccommodationMultiplicationTable},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_SC_Writitems', 'target': AssessmentHeaders.AccommodationScribe},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_STT', 'target': AssessmentHeaders.AccommodationSpeechToText},
    {'type': 'NonEmbeddedAccommodations', 'code': 'NEA_NoiseBuf', 'target': AssessmentHeaders.AccommodationNoiseBuffer}]


def get_accommodations(opportunity):
    '''
     Get accommodations from XML.

     We have two categories of accommodations: Embbed and NonEmbbedded

     Embbed accommodations include AmericanSignLanguage, ClosedCaptioning, Language, TextToSpeech, StreamlinedInterface, PrintOnDemand(PrintOnDemand + TDS_PoD0), PrintOnDemandItem(PrintOnDemand + TDS_PoD_Stim&TDS_PoD_Item). If any of the above accommodations appears in XML with `context` of value 'FINAL', we look up use code in element <Score measureLabel="Accommodation"/> according to corresponding accommodation type, otherwise use 0 as fallback use code

     Non-Embbed accommodations include Abacus, AlternativeResponse, Calculator, MultiplicationTable, ReadAloud, Scribe, SpeechToText, NoiseBuffer. Each of the above corresponds to a unique code, as in <Accommodation /> 'code' attribute, respectively: NEA_Abacus, NEA_AR, NEA_Calc, NEA_MT, NEA_RA_Stimuli, NEA_SC_WritItems, NEA_STT, NEA_NoiseBuf.
     We look up below element for use code and assign to all Non-Embbed accommodation that show in XML.
         <Score measureOf="NonEmbeddedAccommodations" measureLabel="Accommodation" value="6" />
     All presented Non-Embbed Accommodations will have the same use code, otherwise use 0 as fallback use code
     However, there's a special Non-Embbed code 'NEA0', which is mutually exclusive with the others. In case of its presence, all Non-Embbed accommodations should be assigned with value 0 in database.
    '''
    USE_CODE_NO_ACCESS = '4'
    USE_CODE_NO_MESSAGE = '0'

    def _format_XPath(config):
        score_xpath = "./Score/[@measureOf='%s'][@measureLabel='Accommodation']" % config['type']
        acc_xpath = "./Accommodation/[@type='%s'][@context='FINAL']" % config['type']
        if 'code' in config:
            acc_xpath += "[@code='%s']" % config['code']
        return acc_xpath, score_xpath

    def _has_NEA0(opportunity):
        acc_xpath, _ = _format_XPath({'type': 'NonEmbeddedAccommodations', 'code': 'NEA0'})
        return opportunity.find(acc_xpath) is not None

    def _is_non_embbed(config):
        return config['type'] == 'NonEmbeddedAccommodations'

    accommodations = []
    hasNEA0 = _has_NEA0(opportunity)
    for config in ACCOMMODATION_CONFIGS:
        if _is_non_embbed(config) and hasNEA0:
            use_code = USE_CODE_NO_ACCESS
        else:
            acc_xpath, score_xpath = _format_XPath(config)
            score = opportunity.find(score_xpath) if opportunity.find(acc_xpath) is not None else None
            use_code = score.get('value') if score is not None else USE_CODE_NO_MESSAGE
        accommodations.append(Mapping(ValueMeta(use_code), config['target']))
    return accommodations


def get_claims(metadata_file_path, opportunity):
    # read metadata and map Claim1, Claim2, Claim3, and Claim4
    metadata = None
    with open(metadata_file_path) as f:
        metadata_json = f.read()
        metadata = json.loads(metadata_json)

    claim1_mapping = getClaimMappingName(metadata, PerformanceMetadataConstants.CLAIM1, PerformanceMetadataConstants.CLAIM1) or get_claim1_mapping(opportunity)
    claim2_mapping = getClaimMappingName(metadata, PerformanceMetadataConstants.CLAIM2, PerformanceMetadataConstants.CLAIM2)
    claim3_mapping = getClaimMappingName(metadata, PerformanceMetadataConstants.CLAIM3, PerformanceMetadataConstants.CLAIM3)
    claim4_mapping = getClaimMappingName(metadata, PerformanceMetadataConstants.CLAIM4, PerformanceMetadataConstants.CLAIM4)

    if not claim1_mapping:
        raise MetadataException("Incorrect claims number of assessment type %s" % metadata['Identification']['Type'])

    overall_score = XMLClaimScore(opportunity, "./Score/[@measureOf='Overall'][@measureLabel='ScaleScore']", "value", "standardError")
    claim1_score = XMLClaimScore(opportunity, "./Score/[@measureOf='" + claim1_mapping + "'][@measureLabel='ScaleScore']", "value", "standardError")
    claim2_score = XMLClaimScore(opportunity, "./Score/[@measureOf='" + claim2_mapping + "'][@measureLabel='ScaleScore']", "value", "standardError")
    claim3_score = XMLClaimScore(opportunity, "./Score/[@measureOf='" + claim3_mapping + "'][@measureLabel='ScaleScore']", "value", "standardError")
    claim4_score = XMLClaimScore(opportunity, "./Score/[@measureOf='" + claim4_mapping + "'][@measureLabel='ScaleScore']", "value", "standardError")

    return [
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Overall'][@measureLabel='ScaleScore']", "value"), AssessmentHeaders.AssessmentSubtestResultScoreValue),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Overall'][@measureLabel='PerformanceLevel']", "value"), AssessmentHeaders.AssessmentPerformanceLevelIdentifier),
        Mapping(overall_score.get_min(), AssessmentHeaders.AssessmentSubtestMinimumValue),
        Mapping(overall_score.get_max(), AssessmentHeaders.AssessmentSubtestMaximumValue),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim1_mapping + "'][@measureLabel='ScaleScore']", "value"), AssessmentHeaders.AssessmentSubtestResultScoreClaim1Value),
        Mapping(claim1_score.get_min(), AssessmentHeaders.AssessmentSubtestClaim1MinimumValue),
        Mapping(claim1_score.get_max(), AssessmentHeaders.AssessmentSubtestClaim1MaximumValue),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim1_mapping + "'][@measureLabel='PerformanceLevel']", "value"), AssessmentHeaders.AssessmentClaim1PerformanceLevelIdentifier),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim2_mapping + "'][@measureLabel='ScaleScore']", "value"), AssessmentHeaders.AssessmentSubtestResultScoreClaim2Value),
        Mapping(claim2_score.get_min(), AssessmentHeaders.AssessmentSubtestClaim2MinimumValue),
        Mapping(claim2_score.get_max(), AssessmentHeaders.AssessmentSubtestClaim2MaximumValue),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim2_mapping + "'][@measureLabel='PerformanceLevel']", "value"), AssessmentHeaders.AssessmentClaim2PerformanceLevelIdentifier),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim3_mapping + "'][@measureLabel='ScaleScore']", "value"), AssessmentHeaders.AssessmentSubtestResultScoreClaim3Value),
        Mapping(claim3_score.get_min(), AssessmentHeaders.AssessmentSubtestClaim3MinimumValue),
        Mapping(claim3_score.get_max(), AssessmentHeaders.AssessmentSubtestClaim3MaximumValue),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim3_mapping + "'][@measureLabel='PerformanceLevel']", "value"), AssessmentHeaders.AssessmentClaim3PerformanceLevelIdentifier),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim4_mapping + "'][@measureLabel='ScaleScore']", "value"), AssessmentHeaders.AssessmentSubtestResultScoreClaim4Value),
        Mapping(claim4_score.get_min(), AssessmentHeaders.AssessmentSubtestClaim4MinimumValue),
        Mapping(claim4_score.get_max(), AssessmentHeaders.AssessmentSubtestClaim4MaximumValue),
        Mapping(XMLMeta(opportunity, "./Score/[@measureOf='" + claim4_mapping + "'][@measureLabel='PerformanceLevel']", "value"), AssessmentHeaders.AssessmentClaim4PerformanceLevelIdentifier)
    ]


def get_claim1_mapping(opportunity):
    # if no claims mapping found, we take the first non-Overall
    # score element with measureLabel 'ScaleScore' and map to claim1
    claims = opportunity.findall("./Score/[@measureLabel='ScaleScore']") or []
    claims = [claim for claim in claims if claim.get('measureOf') != 'Overall']
    if len(claims) != 1:
        return None
    return claims[0].get('measureOf')
