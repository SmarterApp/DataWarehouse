'''
Created on Aug 8, 2014

@author: dip
'''
from edcore.utils.utils import merge_dict, reverse_map
from smarter_score_batcher.utils.xml_utils import extract_meta_with_fallback_helper,\
    extract_meta_without_fallback_helper


class XMLMeta:
    def __init__(self, root, xpath, attribute, attribute_to_compare=None):
        self.__root = root
        self.__path = xpath
        self.__attribute = attribute
        self.__attribute_to_compare = attribute_to_compare

    def get_value(self):
        if self.__attribute_to_compare:
            val = extract_meta_with_fallback_helper(self.__root, self.__path, self.__attribute, self.__attribute_to_compare)
        else:
            val = extract_meta_without_fallback_helper(self.__root, self.__path, self.__attribute)
        return val


class AccommodationMeta:
    def __init__(self, root, attribute):
        self._root = root
        self._attribute = attribute

    def get_value(self):
        # TODO:  Some defaults are different
        val = '0'
        for element in self._root:
            if element.get('type') == self._attribute:
                return element.get('value')
        return val


class Mapping:
    def __init__(self, src, target):
        self.src = src
        self.target = target

    def evaluate(self):
        return {self.target: self.src.get_value()}


class CSVHeaders:
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
    AccommodationSignLanguageHumanIntervention = 'AccommodationSignLanguageHumanIntervention'
    AccommodationBraille = 'AccommodationBraille'
    AccommodationClosedCaptioning = 'AccommodationClosedCaptioning'
    AccommodationTextToSpeech = 'AccommodationTextToSpeech'
    AccommodationAbacus = 'AccommodationAbacus'
    AccommodationAlternateResponseOptions = 'AccommodationAlternateResponseOptions'
    AccommodationCalculator = 'AccommodationCalculator'
    AccommodationMultiplicationTable = 'AccommodationMultiplicationTable'
    AccommodationPrintOnDemand = 'AccommodationPrintOnDemand'
    AccommodationReadAloud = 'AccommodationReadAloud'
    AccommodationScribe = 'AccommodationScribe'
    AccommodationSpeechToText = 'AccommodationSpeechToText'
    AccommodationStreamlineMode = 'AccommodationStreamlineMode'


#def get_accomodation_mapping(root):
#    '''
#    Accomodation has 0 to many nodes in XML
#    '''
#    # TODO:  Use this instead?
#    accommodation = root.findall("./Accommodation")
#    # mapping from XML to CSV
#    mapping = {'AmericanSignLanguage': CSVHeaders.AccommodationAmericanSignLanguage,
#               'AmericanSignLanguageInterpreter': CSVHeaders.AccommodationSignLanguageHumanIntervention,
#               'Braile': CSVHeaders.AccommodationBraille,
#               'ClosedCaptioning': CSVHeaders.AccommodationClosedCaptioning,
#               'TTS': CSVHeaders.AccommodationTextToSpeech,
#               'Abacus': CSVHeaders.AccommodationAbacus,
#               'AlternateResponseOptions': CSVHeaders.AccommodationAlternateResponseOptions,
#               'Calculator': CSVHeaders.AccommodationCalculator,
#               'MultiplicationTable': CSVHeaders.AccommodationMultiplicationTable,
#               'PrintOnDemand': CSVHeaders.AccommodationPrintOnDemand,
#               'ReadAloud': CSVHeaders.AccommodationReadAloud,
#               'Scribe': CSVHeaders.AccommodationScribe,
#               'SpeechToText': CSVHeaders.AccommodationSpeechToText,
#               'StreamlineMode': CSVHeaders.AccommodationStreamlineMode}
#
#    # Reverse it and default to zero
#    accommodation_values = reverse_map(mapping)
#    for k in accommodation_values.keys():
#        # TODO:  Some defaults are different
#        accommodation_values[k] = 0
#
#    for element in accommodation:
#        name = element['type']
#        if name in mapping.keys():
#            accommodation_values[name] = element['value']
#
#    return accommodation_values


def get_csv_mapping(root):
    examinee = root.find("./Examinee")
    accommodation = root.findall("./Opportunity/Accommodation")
    opportunity = root.find("./Opportunity")

    # In the order of the csv headers
    mappings = [Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='StateName']", "value", "context"), CSVHeaders.StateAbbreviation),
                Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='DistrictID']", "value", "context"), CSVHeaders.ResponsibleSchoolIdentifier),
                Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='DistrictName']", "value", "context"), CSVHeaders.OrganizationName),
                Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='SchoolID']", "value", "context"), CSVHeaders.ResponsibleSchoolIdentifier),
                Mapping(XMLMeta(examinee, "./ExamineeRelationship/[@name='SchoolName']", "value", "context"), CSVHeaders.NameOfInstitution),

                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='StudentIdentifier']", "value", "context"), CSVHeaders.StudentIdentifier),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='AlternateSSID']", "value", "context"), CSVHeaders.ExternalSSID),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='FirstName']", "value", "context"), CSVHeaders.FirstName),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='MiddleName']", "value", "context"), CSVHeaders.MiddleName),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='LastOrSurname']", "value", "context"), CSVHeaders.LastOrSurname),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Sex']", "value", "context"), CSVHeaders.Sex),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Birthdate']", "value", "context"), CSVHeaders.Birthdate),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='GradeLevelWhenAssessed']", "value", "context"), CSVHeaders.GradeLevelWhenAssessed),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='HispanicOrLatinoEthnicity']", "value", "context"), CSVHeaders.HispanicOrLatinoEthnicity),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='AmericanIndianOrAlaskaNative']", "value", "context"), CSVHeaders.AmericanIndianOrAlaskaNative),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Asian']", "value", "context"), CSVHeaders.Asian),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='BlackOrAfricanAmerican']", "value", "context"), CSVHeaders.BlackOrAfricanAmerican),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='NativeHawaiianOrOtherPacificIslander']", "value", "context"), CSVHeaders.NativeHawaiianOrOtherPacificIslander),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='White']", "value", "context"), CSVHeaders.White),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='DemographicRaceTwoOrMoreRaces']", "value", "context"), CSVHeaders.DemographicRaceTwoOrMoreRaces),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='IDEAIndicator']", "value", "context"), CSVHeaders.IDEAIndicator),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='LEPStatus']", "value", "context"), CSVHeaders.LEPStatus),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Section504Status']", "value", "context"), CSVHeaders.Section504Status),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='EconomicDisadvantageStatus']", "value", "context"), CSVHeaders.EconomicDisadvantageStatus),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='MigrantStatus']", "value", "context"), CSVHeaders.MigrantStatus),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Group1Id']", "value", "context"), CSVHeaders.Group1Id),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Group1Text']", "value", "context"), CSVHeaders.Group1Text),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Group2Id']", "value", "context"), CSVHeaders.Group2Id),
                Mapping(XMLMeta(examinee, "./ExamineeAttribute/[@name='Group2Text']", "value", "context"), CSVHeaders.Group2Text),

                Mapping(XMLMeta(root, "./Test", "testId"), CSVHeaders.AssessmentGuid),
                Mapping(XMLMeta(opportunity, ".", "oppId"), CSVHeaders.AssessmentSessionLocationId),
                Mapping(XMLMeta(opportunity, ".", "server"), CSVHeaders.AssessmentSessionLocation),
                Mapping(XMLMeta(opportunity, ".", "dateCompleted"), CSVHeaders.AssessmentAdministrationFinishDate),
                Mapping(XMLMeta(root, "./Test", "academicYear"), CSVHeaders.AssessmentYear),
                Mapping(XMLMeta(root, "./Test", "assessmentType"), CSVHeaders.AssessmentType),
                Mapping(XMLMeta(root, "./Test", "subject"), CSVHeaders.AssessmentAcademicSubject),
                Mapping(XMLMeta(root, "./Test", "grade"), CSVHeaders.AssessmentLevelForWhichDesigned),

                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Overall'][@measureLabel='ScaleScore']", "value"), CSVHeaders.AssessmentSubtestResultScoreValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Overall'][@measureLabel='MinScore']", "value"), CSVHeaders.AssessmentSubtestMinimumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Overall'][@measureLabel='MaxScore']", "value"), CSVHeaders.AssessmentSubtestMaximumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Overall'][@measureLabel='PerformanceLevel']", "value"), CSVHeaders.AssessmentPerformanceLevelIdentifier),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim1'][@measureLabel='ScaleScore']", "value"), CSVHeaders.AssessmentSubtestResultScoreClaim1Value),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim1'][@measureLabel='MinScore']", "value"), CSVHeaders.AssessmentSubtestClaim1MinimumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim1'][@measureLabel='MaxScore']", "value"), CSVHeaders.AssessmentSubtestClaim1MaximumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim1'][@measureLabel='PerformanceLevel']", "value"), CSVHeaders.AssessmentClaim1PerformanceLevelIdentifier),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim2'][@measureLabel='ScaleScore']", "value"), CSVHeaders.AssessmentSubtestResultScoreClaim2Value),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim2'][@measureLabel='MinScore']", "value"), CSVHeaders.AssessmentSubtestClaim2MinimumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim2'][@measureLabel='MaxScore']", "value"), CSVHeaders.AssessmentSubtestClaim2MaximumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim2'][@measureLabel='PerformanceLevel']", "value"), CSVHeaders.AssessmentClaim2PerformanceLevelIdentifier),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim3'][@measureLabel='ScaleScore']", "value"), CSVHeaders.AssessmentSubtestResultScoreClaim3Value),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim3'][@measureLabel='MinScore']", "value"), CSVHeaders.AssessmentSubtestClaim3MinimumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim3'][@measureLabel='MaxScore']", "value"), CSVHeaders.AssessmentSubtestClaim3MaximumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim3'][@measureLabel='PerformanceLevel']", "value"), CSVHeaders.AssessmentClaim3PerformanceLevelIdentifier),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim4'][@measureLabel='ScaleScore']", "value"), CSVHeaders.AssessmentSubtestResultScoreClaim4Value),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim4'][@measureLabel='MinScore']", "value"), CSVHeaders.AssessmentSubtestClaim4MinimumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim4'][@measureLabel='MaxScore']", "value"), CSVHeaders.AssessmentSubtestClaim4MaximumValue),
                Mapping(XMLMeta(opportunity, "./Score/[@measureOf='Claim4'][@measureLabel='PerformanceLevel']", "value"), CSVHeaders.AssessmentClaim4PerformanceLevelIdentifier),

                Mapping(AccommodationMeta(accommodation, 'AmericanSignLanguage'), CSVHeaders.AccommodationAmericanSignLanguage),
                Mapping(AccommodationMeta(accommodation, 'AmericanSignLanguageInterpreter'), CSVHeaders.AccommodationSignLanguageHumanIntervention),
                Mapping(AccommodationMeta(accommodation, 'Braile'), CSVHeaders.AccommodationBraille),
                Mapping(AccommodationMeta(accommodation, 'ClosedCaptioning'), CSVHeaders.AccommodationClosedCaptioning),
                Mapping(AccommodationMeta(accommodation, 'TTS'), CSVHeaders.AccommodationTextToSpeech),
                Mapping(AccommodationMeta(accommodation, 'Abacus'), CSVHeaders.AccommodationAbacus),
                Mapping(AccommodationMeta(accommodation, 'AlternateResponseOptions'), CSVHeaders.AccommodationAlternateResponseOptions),
                Mapping(AccommodationMeta(accommodation, 'Calculator'), CSVHeaders.AccommodationCalculator),
                Mapping(AccommodationMeta(accommodation, 'MultiplicationTable'), CSVHeaders.AccommodationMultiplicationTable),
                Mapping(AccommodationMeta(accommodation, 'PrintOnDemand'), CSVHeaders.AccommodationPrintOnDemand),
                Mapping(AccommodationMeta(accommodation, 'ReadAloud'), CSVHeaders.AccommodationReadAloud),
                Mapping(AccommodationMeta(accommodation, 'Scribe'), CSVHeaders.AccommodationScribe),
                Mapping(AccommodationMeta(accommodation, 'SpeechToText'), CSVHeaders.AccommodationSpeechToText),
                Mapping(AccommodationMeta(accommodation, 'StreamlineMode'), CSVHeaders.AccommodationStreamlineMode)]

    values = {}
    for m in mappings:
        values = merge_dict(values, m.evaluate())
    return values
