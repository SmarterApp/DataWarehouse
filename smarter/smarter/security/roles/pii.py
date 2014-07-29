'''
Created on May 9, 2013

@author: dip
'''
from sqlalchemy.sql.expression import and_, or_

from smarter.reports.helpers.constants import Constants
from smarter.security.roles.default import BaseRole
from smarter.security.roles.base import verify_context
from smarter.security.context_role_map import ContextRoleMap
from smarter_common.security.constants import RolesConstants


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
        fact_asmt_outcome_vw = self.connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        context = user.get_context().get_all_context(tenant, self.name)
        if not context:
            # context returned is empty, therefore no context
            return None
        expr = []
        for k, v in context.items():
            if v:
                expr.append(and_(fact_asmt_outcome_vw.c[k].in_(v)))
        return expr

    @verify_context
    def add_context(self, tenant, user, query):
        '''
        Updates a query adding context
        If Context is an empty list, return None, which will return Forbidden Error
        '''
        context = user.get_context().get_all_context(tenant, self.name)
        if not context:
            # context returned is empty, therefore no context
            return None
        expr = []
        for k, v in context.items():
            if v:
                expr.append(*[table.c[k].in_(v) for table in self.get_context_tables(query)])
        return query.where(and_(or_(*expr)))

    def check_context(self, tenant, user, student_ids):
        '''
        Given a list of student guids, return true if user guid has access to those students
        '''
        query = super().get_students(tenant, student_ids)
        query = query.where(or_(*self.get_context(tenant, user)))
        results = self.connector.get_result(query)
        return len(student_ids) == len(results)
