from edcore.database.stats_connector import StatsDBConnection
from edcore.database.utils.constants import UdlStatsConstants


def insert_to_table(conn, table_name, values):
    '''
    Generic Insertion of values into table based on a connection
    '''
    with conn() as connector:
        table = connector.get_table(table_name)
        stmt = table.insert(values)
        connector.execute(stmt)


def update_records_in_table(conn, table_name, values, criteria):
    '''
    Updates record in table with where clause derived from criteria
    '''
    with conn() as connector:
        table = connector.get_table(table_name)
        stmt = table.update().values(values)
        for k, v in criteria.items():
            stmt = stmt.where(table.c[k] == v)
        connector.execute(stmt)


def insert_udl_stats(values):
    '''
    Insert into udl stats table
    '''
    insert_to_table(StatsDBConnection, UdlStatsConstants.UDL_STATS, values)


def update_udl_stats(batch_guid, values):
    '''
    Update udl stats table by batch_guid
    '''
    update_records_in_table(StatsDBConnection, UdlStatsConstants.UDL_STATS, values, {UdlStatsConstants.BATCH_GUID: batch_guid})
