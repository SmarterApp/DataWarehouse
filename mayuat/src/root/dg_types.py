'''
Created on Apr 4, 2013

@author: kallen
'''

GRADES = 'grades'
STUDENTS = 'students'
STATE_TYPE = 'stateType'
DISTRICT_TYPES_AND_COUNTS = 'districtTypesAndCounts'
SCHOOL_COUNTS = 'school_counts'
AVG = 'avg'
SCHOOL_TYPES_AND_RATIOS = 'schoolTypesAndRatios'
PERCENTAGES = 'percentages'
GAMMA = 'gamma'


def getSchoolTypes():
    schoolTypes = {'High': {'grades': [11], 'students': {'min': 100, 'max': 500, 'avg': 300}},
                   'Middle': {'grades': [6, 7, 8], 'students': {'min': 50, 'max': 200, 'avg': 150}},
                   'Elementary': {'grades': [3, 4, 5], 'students': {'min': 20, 'max': 70, 'avg': 60}}
                   }
    return schoolTypes


def getDistrictTypes():
    districtTypes = {'Big': {'school_counts': {'min': 50, 'max': 80, 'avg': 65}, 'schoolTypesAndRatios': {'High': 1, 'Middle': 2, 'Elementary': 5}},
                     'Medium': {'school_counts': {'min': 20, 'max': 24, 'avg': 22}, 'schoolTypesAndRatios': {'High': 1, 'Middle': 2, 'Elementary': 5}},
                     'Small': {'school_counts': {'min': 2, 'max': 8, 'avg': 5}, 'schoolTypesAndRatios': {'High': 1, 'Middle': 2, 'Elementary': 5}}
                     }
    return districtTypes


def getStateTypes():
    stateTypes = {'Typical1': {'districtTypesAndCounts': {'Big': 2, 'Medium': 6, 'Small': 40}, 'subjectsAndPercentages': {'Math': .9, 'ELA': .9}}
                  }
    return stateTypes


def get_scores():
    """ min + max + 3 cut points define 4 pereformance levels
        PL1 = min - cp1 (exclusive)
        PL2 = cp1 - cp2 (exclusive)
        PL3 = cp2 - cp3 (exclusive)
        PL4 = cp3 - max (inclusive)
    """
    scores = {'min': 1200, 'max': 2400, 'cut_points': [1575, 1875, 2175]}
    return scores


def get_error_band():
    eb = {'min_%': 3.125, 'max_%': 12.5, 'random_adjustment_points_lo': -10, 'random_adjustment_points_hi': 25}
    return eb


def get_performance_level_distributions():
    """ Structure is :
        {'assessment-type' : {'grade': {'algorithm': algorithm-parameters}}}
        where 'algorithm' is one of 'percentages' or 'gamma'
        the nature of 'algorithm-parameters' depends on the choice of algorithm
        'percentages': [list of numbers summing to 100]
        'gamma': {'avg': average-value, 'std': standard-deviation} optionally can also have 'min' and 'max' values
    """

    pld = {'ELA': {'3': {'percentages': [30, 34, 28, 9]},
                   '4': {'gamma': {'avg': 1800, 'std': 200}},
                   '5': {'percentages': [27, 38, 29, 6]},
                   '6': {'percentages': [26, 39, 29, 6]},
                   '7': {'percentages': [25, 40, 30, 5]},
                   '8': {'percentages': [23, 42, 31, 4]},
                   '11': {'percentages': [21, 44, 32, 3]}
                   },
           'Math': {'3': {'percentages': [14, 42, 37, 7]},
                    '4': {'percentages': [16, 42, 35, 7]},
                    '5': {'percentages': [18, 41, 33, 8]},
                    '6': {'percentages': [20, 40, 31, 9]},
                    '7': {'percentages': [22, 39, 30, 9]},
                    '8': {'percentages': [24, 38, 29, 9]},
                    '11': {'percentages': [26, 37, 28, 9]}}
           }
    return pld
