'''
Created on May 9, 2013

@author: dip
'''
from smarter.reports.helpers.constants import Constants
from smarter.security.roles.default import BaseRole
from smarter.security.roles.base import verify_context
from smarter.security.context_role_map import ContextRoleMap
from smarter.security.constants import RolesConstants
from sqlalchemy.sql.expression import and_, or_


# PII and SAR Extracts have the same context
@ContextRoleMap.register([RolesConstants.PII, RolesConstants.SAR_EXTRACTS])
class PII(BaseRole):

    def __init__(self, connector, name):
        super().__init__(connector, name)

    @verify_context
    def get_context(self, tenant, user):
        '''
        Returns a sqlalchemy binary expression representing section_guid that user has context to
        If Context is an empty list, return none, which will return Forbidden Error
        '''
        fact_asmt_outcome = self.connector.get_table(Constants.FACT_ASMT_OUTCOME)
        context = user.get_context().get_all_context(tenant, self.name)
        expr = []
        for k, v in context.items():
            if v:
                expr.append(and_(fact_asmt_outcome.c[k].in_(v)))
        return expr

    def check_context(self, tenant, user, student_guids):
        '''
        Given a list of student guids, return true if user guid has access to those students
        '''
        query = super().get_students(tenant, student_guids)
        query = query.where(or_(*self.get_context(tenant, user)))
        results = self.connector.get_result(query)
        return len(student_guids) == len(results)
