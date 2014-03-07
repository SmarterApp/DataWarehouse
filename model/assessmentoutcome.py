"""
Model an assessment outcome (an instance of a student taking an assessment) for the SBAC assessment.

@author: nestep
@date: March 3, 2014
"""

from mongoengine import IntField, ReferenceField

import project.sbac.config.cfg as sbac_config

from general.model.assessmentoutcome import AssessmentOutcome
from project.sbac.model.institutionhierarchy import InstitutionHierarchy


class SBACAssessmentOutcome(AssessmentOutcome):
    """
    The SBAC-specific assessment outcome class.
    """
    inst_hierarchy = ReferenceField(InstitutionHierarchy, required=True)
    overall_score = IntField(required=True, min_value=sbac_config.ASMT_SCORE_MIN,
                             max_value=sbac_config.ASMT_SCORE_MAX)
    overall_score_range_min = IntField(required=True, min_value=sbac_config.ASMT_SCORE_MIN,
                                       max_value=sbac_config.ASMT_SCORE_MAX)
    overall_score_range_max = IntField(required=True, min_value=sbac_config.ASMT_SCORE_MIN,
                                       max_value=sbac_config.ASMT_SCORE_MAX)
    overall_perf_lvl = IntField(required=True, min_value=1, max_value=5)
    claim_1_score = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                             max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_1_score_range_min = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_1_score_range_max = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_1_perf_lvl = IntField(required=True, min_value=1, max_value=5)
    claim_2_score = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                             max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_2_score_range_min = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_2_score_range_max = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_2_perf_lvl = IntField(required=True, min_value=1, max_value=5)
    claim_3_score = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                             max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_3_score_range_min = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_3_score_range_max = IntField(required=True, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_3_perf_lvl = IntField(required=True, min_value=1, max_value=5)
    claim_4_score = IntField(required=False, min_value=sbac_config.CLAIM_SCORE_MIN,
                             max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_4_score_range_min = IntField(required=False, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_4_score_range_max = IntField(required=False, min_value=sbac_config.CLAIM_SCORE_MIN,
                                       max_value=sbac_config.CLAIM_SCORE_MAX)
    claim_4_perf_lvl = IntField(required=False, min_value=1, max_value=5)
    acc_asl_video_embed = IntField(required=False, min_value=0, max_value=10)
    acc_asl_human_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_braile_embed = IntField(required=False, min_value=0, max_value=10)
    acc_closed_captioning_embed = IntField(required=False, min_value=0, max_value=10)
    acc_text_to_speech_embed = IntField(required=False, min_value=0, max_value=10)
    acc_abacus_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_alternate_response_options_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_calculator_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_multiplication_table_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_print_on_demand_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_read_aloud_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_scribe_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_speech_to_text_nonembed = IntField(required=False, min_value=0, max_value=10)
    acc_streamline_mode = IntField(required=False, min_value=0, max_value=10)
    

    def get_object_set(self):
        """
        Get the set of objects that this exposes to a CSV or JSON writer.

        @returns: Dictionary of root objects
        """
        return {'state': self.student.school.district.state,
                'district': self.student.school.district,
                'school': self.student.school,
                'student': self.student,
                'section': self.section,
                'institution_hierarchy': self.inst_hierarchy,
                'assessment': self.assessment,
                'assessment_outcome': self}