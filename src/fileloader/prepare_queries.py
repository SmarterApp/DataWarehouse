from udl2_util.measurement import measure_cpu_plus_elasped_time


@measure_cpu_plus_elasped_time
def create_fdw_extension_query(csv_schema):
    return "CREATE EXTENSION IF NOT EXISTS file_fdw WITH SCHEMA {csv_schema}".format(csv_schema=csv_schema)


@measure_cpu_plus_elasped_time
def create_fdw_server_query(fdw_server):
    return "CREATE SERVER {fdw_server} FOREIGN DATA WRAPPER file_fdw".format(fdw_server=fdw_server)


@measure_cpu_plus_elasped_time
def create_ddl_csv_query(header_names, header_types, csv_file, csv_schema, csv_table, fdw_server):
    ddl_parts = ["CREATE FOREIGN TABLE IF NOT EXISTS \"%s\".\"%s\" ( " % (csv_schema, csv_table),
                 ','.join([header_names[i] + ' ' + header_types[i] + ' ' for i in range(len(header_names))]),
                 ") SERVER %s " % fdw_server,
                 "OPTIONS (filename '%s', format '%s', header '%s')" % (csv_file, 'csv', 'false')]
    ddl_parts = "".join(ddl_parts)
    # print(ddl_parts)
    return ddl_parts


@measure_cpu_plus_elasped_time
def drop_ddl_csv_query(csv_schema, csv_table):
    ddl = 'DROP FOREIGN TABLE IF EXISTS "{csv_schema}"."{csv_table}"'.format(csv_schema=csv_schema, csv_table=csv_table)
    return ddl


@measure_cpu_plus_elasped_time
def create_staging_tables_query(header_types, header_names, csv_file, staging_schema, staging_table):
    # TODO: need to be replaced by importing from staging table definition
    ddl_parts = ["CREATE TABLE IF NOT EXISTS %s.%s (" % (staging_schema, staging_table),
                 ','.join([header_names[i] + ' ' + header_types[i] for i in range(len(header_names))]),
                 ") "]
    return "".join(ddl_parts)


@measure_cpu_plus_elasped_time
def drop_staging_tables_query(csv_schema, csv_table):
    ddl = 'DROP TABLE IF EXISTS "{csv_schema}"."{csv_table}"'.format(csv_schema=csv_schema, csv_table=csv_table)
    return ddl


@measure_cpu_plus_elasped_time
def create_inserting_into_staging_query(stg_asmt_outcome_columns, apply_rules, csv_table_columns, header_types, staging_schema,
                                        staging_table, csv_schema, csv_table, start_seq, seq_name, transformation_rules):
    column_names_with_proc = apply_transformation_rules(apply_rules, header_types, csv_table_columns, transformation_rules)
    insert_sql = ["INSERT INTO \"{staging_schema}\".\"{staging_table}\"(",
                   ",".join(stg_asmt_outcome_columns),
                   ") SELECT ",
                   ",".join(column_names_with_proc),
                   " FROM \"{csv_schema}\".\"{csv_table}\"",
                   ]
    insert_sql = "".join(insert_sql).format(seq_name=seq_name, staging_schema=staging_schema, staging_table=staging_table,
                                            csv_schema=csv_schema, csv_table=csv_table)
    return insert_sql


@measure_cpu_plus_elasped_time
def create_insert_assessment_into_integration_query(header, data, batch_id, int_schema, int_table):
    insert_sql = ['INSERT INTO "{int_schema}"."{int_table}"(',
                  ','.join(header),
                  ')',
                  'VALUES (',
                  ','.join(data),
                  ')']
    insert_sql = ''.join(insert_sql).format(int_schema=int_schema, int_table=int_table)
    # print(insert_sql)
    return insert_sql


@measure_cpu_plus_elasped_time
def set_sequence_query(staging_table, start_seq):
    return "SELECT pg_catalog.setval(pg_get_serial_sequence('{staging_table}', 'src_row_number'), {start_seq}, false)".format(staging_table=staging_table,
                                                                                                                              start_seq=start_seq)


@measure_cpu_plus_elasped_time
def create_sequence_query(staging_schema, seq_name, start_seq):
    return 'CREATE SEQUENCE "{staging_schema}"."{seq_name}" START {start_seq}'.format(staging_schema=staging_schema,
                                                                                      seq_name=seq_name,
                                                                                      start_seq=start_seq)


@measure_cpu_plus_elasped_time
def drop_sequence_query(staging_schema, seq_name):
    return 'DROP SEQUENCE "{staging_schema}"."{seq_name}"'.format(staging_schema=staging_schema,
                                                                  seq_name=seq_name)


@measure_cpu_plus_elasped_time
def apply_transformation_rules(apply_rules, header_types, csv_table_columns, transformation_rules):
    '''
    The function apply the some transformation rules
    '''
    header_with_rules = []
    for i in range(len(csv_table_columns)):
        header_name = csv_table_columns[i]
        rule = transformation_rules[i]
        column_with_rule = header_name
        if apply_rules:
            if rule is not None and rule != '':
                column_with_rule = ''.join([rule, '(', header_name, ')'])
            """
            header_type = header_types[i]
            # test for function map_gender. Hard code as a temporary solution
            if header_name.lower() in ['gender_1', 'gender_2', 'gender_3', 'gender_4']:
                header_name = 'map_gender(' + header_name + ')'
                # test for function map_yn. Hard code as a temporary solution
            elif header_name.lower() in ['y_or_n_1', 'y_or_n_2', 'y_or_n_3', 'y_or_n_4']:
                header_name = 'map_yn(' + header_name + ')'
            elif header_type.lower() == 'text':
                header_name = "trim(replace(upper(" + header_name + "), CHR(13), ''))"

        header_with_rules.append(header_name)
        """
        header_with_rules.append(column_with_rule)
    return header_with_rules


@measure_cpu_plus_elasped_time
def get_column_mapping_query(staging_schema, ref_table, source_table):
    return "SELECT source_column, target_column, stored_proc_name FROM \"{staging_schema}\".\"{ref_table}\" WHERE source_table='{source_table}'".format(staging_schema=staging_schema,
                                                                                                                                                        ref_table=ref_table,
                                                                                                                                                        source_table=source_table)
