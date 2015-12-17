#@PydevCodeAnalysisIgnore
from edudl2.rule_maker.rules.rule_keys import *

#===============================================================================
# Note:
# 1) rule 'calcWeight' would not work for Math, since math has only three claims and the rule checks and calculates if the passed arguments
#     are not null and are numbers. This rule takes in three claim weights and calculates the fourth. (Math does not have a fourth claim)
#     As such the rule works for ELA with four claims. We still keep the rule added for demo purposes.
#===============================================================================

CLEANERS = set([PCLEAN, VCLEAN, RCLEAN])

transform_rules = {'clean': {PCLEAN: [REMNL, TRIM]},
                   'cleanUpper': {PCLEAN: [UPPER, REMNL, TRIM]},
                   'cleanLower': {PCLEAN: [LOWER, REMNL, TRIM]},
                   'date': {DATE: {DATEIN: ['YYYY-MM-DD', 'YYYYMMDD', 'DD Month YYYY', 'DD Mon YY', 'MM-DD-YYYY'],
                                   DATEOUT: 'YYYYMMDD'}},
                   'srDate': {DATE: {DATEIN: ['YYYY-MM-DD'], DATEOUT: 'YYYYMMDD'}},
                   'schoolType': {PCLEAN: [UPPER, REMNL, TRIM],
                                  LOOKUP: {'High School': ['HS', 'HIGH SCHOOL'],
                                           'Middle School': ['MS', 'MIDDLE SCHOOL'],
                                           'Elementary School': ['ES', 'ELEMENTARY SCHOOL']}},
                   'yn': {PCLEAN: [UPPER, REMNL, TRIM],
                          LOOKUP: {'Y': ['Y', '1', 'T'], 'N': ['N', '0', 'F']}},
                   'srYn': {PCLEAN: [UPPER, REMNL, TRIM], LOOKUP: {'Y': ['YES'], 'N': ['NO']}},
                   'gender': {PCLEAN: [UPPER, REMNL, TRIM],
                              INLIST: ['M', 'B', 'MALE', 'BOY', 'F', 'G', 'FEMALE', 'GIRL', 'NS', 'NOT_SPECIFIED', 'NOT SPECIFIED'],
                              OUTLIST: ['male', 'male', 'male', 'male', 'female', 'female', 'female', 'female', 'NS', 'NS', 'NS']},
                   'administrationCondition': {PCLEAN: [UPPER, REMNL, TRIM],
                                               LOOKUP: {'SD': ['SD', 'sd'],
                                                        'IN': ['IN', 'in'],
                                                        'NS': ['NS', 'ns']}},
                   'complete': {PCLEAN: [UPPER, REMNL, TRIM],
                                LOOKUP: {'Y': ['COMPLETE', 'complete'],
                                         'N': ['PARTIAL', 'partial']}},
                   'srGender': {PCLEAN: [UPPER, REMNL, TRIM],
                                INLIST: ['MALE', 'FEMALE'],
                                OUTLIST: ['male', 'female']},
                   'grade': {INLIST: ['13', '12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1'],
                             OUTLIST: ['13', '12', '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01']},
                   'calcWeight': {CALCULATE: '( 1 - ( {claim_1} + {claim_2} + {claim_3} ) )',
                                  PCLEAN: [TRIM, REMNL],
                                  VCLEAN: UPPER,
                                  RCLEAN: [TO_CHAR, MIN0]},
                   'asmtType': {PCLEAN: [UPPER, REMNL, TRIM],
                                LOOKUP: {'SUMMATIVE': ['SUMMATIVE'],
                                         'INTERIM COMPREHENSIVE': ['INTERIM COMPREHENSIVE'],
                                         'INTERIM ASSESSMENT BLOCKS': ['INTERIM ASSESSMENT BLOCKS', 'INTERIM ASSESSMENT BLOCK']}},
                   'subjectType': {PCLEAN: [REMNL, TRIM],
                                   LOOKUP: {'Math': ['MATH', 'MATHS', 'math', 'maths', 'MATHEMATICS', 'Math'],
                                            'ELA': ['ela', 'Ela', 'English Language Arts', 'ELA']}},
                   'option': {PCLEAN: [UPPER, REMNL, TRIM],
                              LOOKUP: {'C': ['C', 'I', None], 'W': ['D']}},
                   }
