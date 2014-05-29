"""
File Content Validator performs content validations on the staged data

Some of the basic validations include (but not limited to)
a) Ensures the asmt_guid coming from json and csv match for all rows in the csv
"""

from edudl2.database.udl2_connector import get_udl_connection
from edudl2.exceptions.errorcodes import ErrorCode
from edudl2.udl2 import message_keys as mk
from sqlalchemy.sql.expression import select
from edudl2.udl2.constants import Constants
from edudl2.udl2_util.exceptions import UDL2InvalidJSONCSVPairException


class ISValidAssessmentPair():
    """Ensures the asmt(Json) and asmt_outcome(csv) records conforms to the same Assessment"""

    @staticmethod
    def execute(conf):
        """
        Ensures the asmt_guid for all the records in the asmt_outcome matches with the asmt_guid in asmt table
        @return: status code: String
        """
        with get_udl_connection() as conn:
            asmt_table = conn.get_table(conf.get(mk.ASMT_TABLE))
            asmt_outcome_table = conn.get_table(conf.get(mk.ASMT_OUTCOME_TABLE))
            asmt_row = conn.get_result(select([asmt_table.c.guid_asmt]).
                                       where(asmt_table.c.guid_batch == conf.get(mk.GUID_BATCH)))
            asmt_outcome_row = conn.get_result(select([asmt_outcome_table.c.guid_asmt], distinct=True).
                                               where(asmt_table.c.guid_batch == conf.get(mk.GUID_BATCH)))
            if 1 != len(asmt_row) or 1 != len(asmt_outcome_row) \
                    or asmt_row[0].get(Constants.GUID_ASMT) != asmt_outcome_row[0].get(Constants.GUID_ASMT):
                raise UDL2InvalidJSONCSVPairException('Assessment guid mismatch between Json/Csv pair for '
                                                      'batch {guid_batch}'.format(guid_batch=conf.get(mk.GUID_BATCH)))
        return ErrorCode.STATUS_OK


class ContentValidator():
    """Determines the file extension and invokes a suite of validations"""

    def __init__(self):
        """Initialize all the data validators"""
        self.validators = [ISValidAssessmentPair()]

    def execute(self, conf):
        """
        :return: list of status codes: [status_code_1, status_code_2]
        """
        # Get the corresponding validator and check
        error_list = []
        for validator in self.validators:
            result = validator.execute(conf)
            if result != ErrorCode.STATUS_OK:
                error_list.append(result)
        return error_list
