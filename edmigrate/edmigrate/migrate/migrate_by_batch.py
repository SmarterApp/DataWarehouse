from edcore.database.utils.constants import UdlStatsConstants
from edmigrate.migrate.migrate_helper import yield_rows
from sqlalchemy.sql.expression import select, and_

__author__ = 'ablum'


def migrate_by_batch(dest_connector, source_connector, table_name, batch_op, batch_criteria, batch_size):
    delete_count, insert_count = 0, 0

    if batch_op == UdlStatsConstants.SNAPSHOT:
        delete_count, insert_count = _migrate_snapshot(dest_connector, source_connector, table_name, batch_criteria, batch_size)

    return delete_count, insert_count


def _migrate_snapshot(dest_connector, source_connector, table_name, batch_criteria, batch_size):
    """
    Migrate a table snapshot as part of a migration by batch.

    @param dest_connector: Destination DB connector
    @param source_connector: Source DB connector
    @param table_name: Name of table to migrate
    @param batch_criteria: Deletion criteria for destination table.

    @return: Deletion and insertion row counts
    """

    # Delete old rows.
    dest_table = dest_connector.get_table(table_name)
    delete_criteria = ['{col}={val}'.format(col=k, val=v.replace('"', "'"))
                       for k, v in (item.split(':') for item in batch_criteria.split(','))]
    delete_query = dest_table.delete().where(and_(" AND ".join(delete_criteria)))
    delete_count = dest_connector.execute(delete_query).rowcount

    # Insert new rows.
    source_table = source_connector.get_table(table_name)
    batched_rows = yield_rows(source_connector, select([source_table]), batch_size)

    insert_count = 0
    for rows in batched_rows:
        insert_query = dest_table.insert()
        insert_count += dest_connector.execute(insert_query, rows).rowcount

    return delete_count, insert_count
