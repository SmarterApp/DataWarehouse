from gen_assessment_outcome import generate_assessment_outcomes
from get_list_of_students import get_students_for_assessment
from gen_assessments import generate_dim_assessment
import argparse
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData
from datetime import datetime

DBDRIVER = "postgresql+pypostgresql"


def generate_fao_from_enrollment(assessment_list, grade, subject, inst_hier_rec_id, where_taken, schema_name,
                                 metadata, db_connection):
    # Main function, will delegate calls to appropriate functions
    rows = get_student_list_from_db(schema_name, metadata, db_connection)
    students = cast_rows_to_students(rows)
    generate_assessment_outcomes(assessment_list, students, grade, subject, inst_hier_rec_id, where_taken)


def get_student_list_from_db(schema_name, metadata, db_connection):
    # Will return a student list from the database.
    students = get_students_for_assessment(schema_name, metadata, db_connection)


def cast_rows_to_students(rows):
    # Turn a dim_student row into a Student object
    pass


def get_input_args():
    '''
    Creates parser for command line arguments
    RETURNS vars(arguments) -- A dictionary of the command line arguments
    '''
    parser = argparse.ArgumentParser(description='Get list of students for assessment generation')
    # database related arguments
    parser.add_argument("-s", "--schema", help="set schema name.  required")
    parser.add_argument("-d", "--database", default="edware", help="set database name default[edware]")
    parser.add_argument("--host", default="127.0.0.1:5432", help="postgre host default[127.0.0.1:5432]")
    parser.add_argument("-u", "--user", default="postgres", help="postgre username default[edware]")
    parser.add_argument("-p", "--password", default="3423346", help="postgre password default[edware]")

    # query related arguments
    parser.add_argument('--state_code', help='set state code.', required=False)
    parser.add_argument('--district_id', help='set district id.', required=False)
    parser.add_argument('--school_id', help='set school id.', required=False)
    parser.add_argument('--section_id', help='set section id.', required=False)
    parser.add_argument('--grade', help='set grade id.', required=False)

    args = parser.parse_args()

    return vars(args)


def main():
    '''
    Entry point main method
    '''
    # Get command line arguments
    input_args = get_input_args()

    # Check for required value of schema
    if input_args['schema'] is None:
        print("Please specify --schema option")
        exit(-1)
    else:
        schema = input_args['schema']

        # Have SQLAlchemy connect to and reflect the database, get the input schema
        db_string = DBDRIVER + '://{user}:{password}@{host}/{database}'.format(**input_args)
        engine = create_engine(db_string)
        db_connection = engine.connect()
        metadata = MetaData(schema=schema)
        metadata.reflect(engine)

        # Get list of students in database
        print("Starting get list of students")
        start_time = datetime.now()
        # student_list = get_students_for_assessment(schema, metadata, db_connection, input_args)
        assessment_list = generate_dim_assessment()
        generate_fao_from_enrollment(assessment_list, grade, subject, inst_hier_rec_id, where_taken, schema_name,
                                     metadata, db_connection)
        finish_time = datetime.now()
        print("Length of student list is ", len(student_list))
        print("Start  at -- ", start_time)
        print("Finish at -- ", finish_time)

        # Close database connection
        db_connection.close()

if __name__ == '__main__':
    main()
