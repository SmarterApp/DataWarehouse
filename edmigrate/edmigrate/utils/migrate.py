from edmigrate.exceptions import EdMigrateRecordAlreadyDeletedException, \
    EdMigrateUdl_statException, EdMigrateException
from sqlalchemy.sql.expression import select, and_, func
from edmigrate.utils.constants import Constants
from edcore.database.stats_connector import StatsDBConnection
from edmigrate.database.migrate_source_connector import EdMigrateSourceConnection
from edmigrate.database.migrate_dest_connector import EdMigrateDestConnection
import logging
from edcore.database.utils.constants import UdlStatsConstants
from edcore.database import initialize_db
import configparser
import sys

__author__ = 'sravi'
# This is a hack needed for now for migration.
# These tables will be dropped in future
# CR, remove this line after dim_section is removed from database
TABLES_NOT_CONNECTED_WITH_BATCH = [Constants.DIM_SECTION]
logger = logging.getLogger('edmigrate')


def get_batches_to_migrate(tenant=None):
    """ This function returns daily batches to be migrated for a given tenant

    :param tenant: The tenant to be migrated
    :type tenant: str
    :returns: A dict mapping batch_guid to the row in udl_daily_stats table
            {'f340322f-b0a8-44df-97bb-6a1f53c4ba48': OrderedDict([
                    ('batch_guid','f340322f-b0a8-44df-97bb-6a1f53c4ba48'),
                    ('tenant','ca'),
                    ('state_code','ca'),
                    ('record_loaded_count',100)
                ]),
                'g344322h-p0at-44df-97bb-8a1e53c1ba90': OrderedDict([
                    ('batch_guid','g344322h-p0at-44df-97bb-8a1e53c1ba90'),
                    ('tenant','ca'),
                    ('state_code','ca'),
                    ('record_loaded_count',150)
            ])}
            An empty dict if no batches found to be migrated
    """
    logger.info('Master: Getting daily delta batches to migrate')

    batches = []
    with StatsDBConnection() as connector:
        udl_status_table = connector.get_table(UdlStatsConstants.UDL_STATS)
        query = \
            select([udl_status_table.c.batch_guid,
                    udl_status_table.c.tenant,
                    udl_status_table.c.state_code,
                    udl_status_table.c.record_loaded_count,
                    udl_status_table.c.load_status,
                    udl_status_table.c.load_start,
                    udl_status_table.c.load_end],
                   from_obj=[udl_status_table]).\
            where(and_(udl_status_table.c.load_type == UdlStatsConstants.LOAD_TYPE_ASSESSMENT, udl_status_table.c.load_status == UdlStatsConstants.UDL_STATUS_INGESTED)).\
            order_by(udl_status_table.c.file_arrived)
        if tenant:
            query = query.where(and_(udl_status_table.c.tenant == tenant))
        batches = connector.get_result(query)
            # batches[row[Constants.BATCH_GUID]] = row
    return batches


def report_udl_stats_batch_status(batch_guid, migrate_load_status):
    """This method populates udl_stats for batches that had successful migration

    :param batch_guid: The batch that was successfully migrated
    :returns : Nothing
    """
    rowcount = 0
    logger.info('Master: Reporting batch status to udl_stats')
    with StatsDBConnection() as connector:
        udl_stats_table = connector.get_table(UdlStatsConstants.UDL_STATS)
        update_query = udl_stats_table.update().values(load_status=migrate_load_status).\
            where(udl_stats_table.c.batch_guid == batch_guid)
        rtn = connector.execute(update_query)
        rowcount = rtn.rowcount
        if rowcount == 0:
            raise EdMigrateUdl_statException('Failed to update record for batch_guid=' + batch_guid)
    return rowcount


def get_tables_to_migrate(connector, batch_guid):
    """This function returns list of tables to be migrated based on schema metadata

    :param connector: The connection to the database
    :returns : A list of table names
             [dim_section, dim_student, fact_asmt_outcome]
    """
    all_tables = []
    for table in connector.get_metadata().tables.keys():
        if '.' in table:
            all_tables.append(table.split('.')[1])
        else:
            all_tables.append(table)
    return all_tables


def yield_rows(connector, query, batch_size):
    """stream the query results in batches of batch_size

    :param connector: The connection to the database
    :param query: The query to be executed
    :param batch_size: The batch_size for streaming
    :returns : Yields a batch of rows
    """
    result = connector.execute(query, stream_results=True)
    rows = result.fetchmany(batch_size)
    while len(rows) > 0:
        yield rows
        rows = result.fetchmany(batch_size)


def get_source_query(source_tab, batch_guid, migrate_all=False):
    """Returns the source query to fetch records from pre-prod

    :param source_tab: Source table to be queried for
    :param batch_guid: Batch Guid of the batch under migration
    :param migrate_all: Flag to ignore batch_guid if set to true

    :returns Sql alchemy query object
    """
    # hack for now to allow dim_section migration (fake record) with out batch_guid matching
    if migrate_all is True:
        return source_tab.select()
    return source_tab.select().where(source_tab.c.batch_guid == batch_guid)


def migrate_dims_insert(batch_guid, schema_name, source_connector, dest_connector, table_name, batch_size=100):
    """Load prod fact table with delta from pre-prod

    :param batch_guid: Batch Guid of the batch under migration
    :param schema_name: Schema name for this batch
    :param source_connector: Source connection
    :param dest_connector: Destination connection
    :param table_name: name of the table to be migrated
    :param batch_size: batch size for migration

    :returns Nothing
    """
    source_tab = source_connector.get_table(table_name, schema_name=schema_name)
    dest_Tab = dest_connector.get_table(table_name)

    if table_name not in TABLES_NOT_CONNECTED_WITH_BATCH:
        query = get_source_query(source_tab, batch_guid)
        # get handle to query result iterator
        rows = yield_rows(source_connector, query, batch_size)
        for batch in rows:
            # execute insert to target schema in batches
            logger.info('Bulk Inserting batch of size: ' + str(len(batch)))
            dest_connector.execute(dest_Tab.insert(), False, batch)


def migrate_fact_asmt_outcome(batch_guid, schema_name, source_connector, dest_connector, batch_size=100):
    """Load prod fact table with delta from pre-prod

    :param batch_guid: Batch Guid of the batch under migration
    :param schema_name: Schema name for this batch
    :param source_connector: Source connection
    :param dest_connector: Destination connection
    :param table_name: name of the table to be migrated
    :param batch_size: batch size for migration

    :returns number of record updated
    """
    delete_count = 0
    insert_count = 0
    source_fact_asmt_outcome_table = source_connector.get_table(Constants.FACT_ASMT_OUTCOME, schema_name=schema_name)

    # CR, change to use PK instead of specific field name.
    delete_query = select([source_fact_asmt_outcome_table.c.asmnt_outcome_rec_id]).\
        where(and_(source_fact_asmt_outcome_table.c.batch_guid == batch_guid,
                   source_fact_asmt_outcome_table.c.status == 'D'))
    # get handle to query result iterator
    proxy_rows = yield_rows(source_connector, delete_query, batch_size)
    temp_asmt_outcome_rec_ids = []
    asmt_outcome_rec_ids = []

    # CR, add comment
    for rows in proxy_rows:
        for row in rows:
            asmt_outcome_rec_id = row[Constants.ASMNT_OUTCOME_REC_ID]
            temp_asmt_outcome_rec_ids.append(asmt_outcome_rec_id)
            asmt_outcome_rec_ids.append(asmt_outcome_rec_id)
            if len(temp_asmt_outcome_rec_ids) >= batch_size:
                delete_count += preprod_to_prod_delete_records(dest_connector, Constants.FACT_ASMT_OUTCOME, Constants.ASMNT_OUTCOME_REC_ID, asmt_outcome_rec_ids)
                del temp_asmt_outcome_rec_ids[:]
    if temp_asmt_outcome_rec_ids:
        delete_count += preprod_to_prod_delete_records(dest_connector, Constants.FACT_ASMT_OUTCOME, Constants.ASMNT_OUTCOME_REC_ID, asmt_outcome_rec_ids)
        del temp_asmt_outcome_rec_ids[:]

    # for Insert
    # CR, change to use PK instead of specific field name.
    insert_query = select([source_fact_asmt_outcome_table.c.asmnt_outcome_rec_id]).\
        where(and_(source_fact_asmt_outcome_table.c.batch_guid == batch_guid,
                   source_fact_asmt_outcome_table.c.status == 'C'))
    # get handle to query result iterator
    proxy_rows = yield_rows(source_connector, insert_query, batch_size)
    # CR, add comment
    for rows in proxy_rows:
        for row in rows:
            asmt_outcome_rec_id = row[Constants.ASMNT_OUTCOME_REC_ID]
            temp_asmt_outcome_rec_ids.append(asmt_outcome_rec_id)
            asmt_outcome_rec_ids.append(asmt_outcome_rec_id)
            if len(temp_asmt_outcome_rec_ids) >= batch_size:
                insert_count += preprod_to_prod_insert_records(schema_name, source_connector, dest_connector, Constants.FACT_ASMT_OUTCOME, Constants.ASMNT_OUTCOME_REC_ID, asmt_outcome_rec_ids)
                del temp_asmt_outcome_rec_ids[:]
    if temp_asmt_outcome_rec_ids:
        insert_count += preprod_to_prod_insert_records(schema_name, source_connector, dest_connector, Constants.FACT_ASMT_OUTCOME, Constants.ASMNT_OUTCOME_REC_ID, asmt_outcome_rec_ids)
        del temp_asmt_outcome_rec_ids[:]
    return delete_count, insert_count


def preprod_to_prod_delete_records(dest_connector, table_name, primary_key_field_name, primary_keys):
    count = 0
    dest_table = dest_connector.get_table(table_name)
    dest_primary_key_field = dest_table.columns[primary_key_field_name]

    update_query = dest_table.update(and_(dest_primary_key_field.in_(primary_keys), dest_table.c.status == 'C')).values(status='D')
    deleted_count = dest_connector.execute(update_query).rowcount
    if deleted_count != len(primary_keys):
        raise EdMigrateRecordAlreadyDeletedException
    else:
        count += deleted_count

    return count


def preprod_to_prod_insert_records(schema_name, source_connector, dest_connector, table_name, primary_key_field_name, primary_keys):
    count = 0
    dest_table = dest_connector.get_table(table_name)
    source_table = source_connector.get_table(table_name, schema_name=schema_name)
    source_primary_key_field = source_table.columns[primary_key_field_name]
    select_query = source_table.select(source_primary_key_field.in_(primary_keys)).where(source_table.c.status == 'C')
    rset = source_connector.execute(select_query)
    rows = rset.fetchall()
    rset.close()
    if rows:
        for row in rows:
            count += dest_connector.execute(dest_table.insert().values(dict(row.items()))).rowcount
    return count


def migrate_all_tables(batch_guid, schema_name, source_connector, dest_connector, tables):
    """Migrate all tables for the given batch from source to destination

    :param batch_guid: Batch Guid of the batch under migration
    :param schema_name: Schema name for this batch
    :param source_connector: Source connection
    :param dest_connector: Destination connection
    :param tables: list of Tables to be migrated

    :returns Nothing
    """
    logger.info('Migrating all tables for batch: ' + batch_guid)
    # migrate dims first
    # CR, check status field, if it does not exist, then call migrate_dims_insert.
    for table in list(filter(lambda x: x.startswith('dim_'), tables)):
        migrate_dims_insert(batch_guid, schema_name, source_connector, dest_connector, table)
    # migrate fact
    migrate_fact_asmt_outcome(batch_guid, schema_name, source_connector, dest_connector)


def migrate_batch(batch):
    """Migrates data for the given batch and given tenant

    :param batch_guid: Batch Guid of the batch under migration
    :param tenant: Tenant name of the tenant to which this batch belongs to
                    This is needed to grab the right source and destination connection

    :returns true: sucess, false: fail (for UT purpose)
    """
    rtn = False
    batch_guid = batch[UdlStatsConstants.BATCH_GUID]
    tenant = batch[UdlStatsConstants.TENANT]
    schema_name = batch[UdlStatsConstants.SCHEMA_NAME]
    logger.info('Migrating batch: ' + batch_guid + ',for tenant: ' + tenant)

    with EdMigrateDestConnection(tenant) as dest_connector, \
            EdMigrateSourceConnection(tenant) as source_connector:
        try:
            # start transaction for this batch
            trans = dest_connector.get_transaction()
            report_udl_stats_batch_status(batch_guid, UdlStatsConstants.MIGRATE_IN_PROCESS)
            tables_to_migrate = get_tables_to_migrate(dest_connector, batch_guid)
            # migrate all tables
            migrate_all_tables(batch_guid, schema_name, source_connector, dest_connector, tables_to_migrate)
            # report udl stats with the new batch migrated
            report_udl_stats_batch_status(batch_guid, UdlStatsConstants.MIGRATE_INGESTED)
            # commit transaction
            trans.commit()
            logger.info('Master: Migration successful for batch: ' + batch_guid)
            rtn = True
        except Exception as e:
            logger.info('Exception happened while migrating batch: ' + batch_guid + ' - Rollback initiated')
            logger.info(e)
            trans.rollback()
            try:
                report_udl_stats_batch_status(batch_guid, UdlStatsConstants.MIGRATE_FAILED)
            except Exception as e:
                pass
    return rtn


def start_migrate_daily_delta(tenant):
    """migration starting point for a tenant

    :param tenant: Tenant name of the tenant to perform the migration

    :returns Nothing
    """
    batches_to_migrate = get_batches_to_migrate(tenant)
    for batch in batches_to_migrate:
        batch[UdlStatsConstants.SCHEMA_NAME] = batch[UdlStatsConstants.BATCH_GUID]
        migrate_batch(batch=batch)

if __name__ == '__main__':
    # TODO: remove this. temp entry point for testing migration as a script
    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    settings = config['app:main']
    initialize_db(EdMigrateDestConnection, settings, allow_schema_create=True)
    initialize_db(EdMigrateSourceConnection, settings, allow_schema_create=True)
    initialize_db(StatsDBConnection, settings, allow_schema_create=True)
    start_migrate_daily_delta('ca')
