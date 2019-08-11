import sqlite3
from datetime import datetime
from castor import bcolors


# create a new .dam file with the initial tables and columns
def create_dam(session_name):
    session = sqlite3.connect(session_name)
    cur = session.cursor()
    create_table = "create table dam (log_name text, line_number numeric, PRIMARY KEY (log_name, line_number))"
    cur.execute(create_table)

    create_table = "create table logs (log_name text PRIMARY KEY, castor_string text, last_line numeric)"
    cur.execute(create_table)
    return session


# load an existing .dam file
def load_dam(session_name):
    session = sqlite3.connect(session_name)
    return session


# add new columns to the dam table
def add_cols(session, cols):
    cur = session.cursor()
    for col in cols:
        cur.execute("alter table dam add column {} text".format(col))


# get all columns in the dam table
def get_cols(session):
    cur = session.cursor()
    cur.execute("PRAGMA table_info(dam)")
    fields = cur.fetchall()
    return [field[1] for field in fields]


# get all columns in the logs table
def get_meta_cols(session):
    cur = session.cursor()
    cur.execute("PRAGMA table_info(logs)")
    fields = cur.fetchall()
    return [field[1] for field in fields]


# get all castor strings associated with logs in this session
def get_castor_strings(session):
    cur = session.cursor()
    cur.execute("select distinct castor_string from logs")
    vals = cur.fetchall()
    return [val[0] for val in vals]


# get all distinct vals for a given column
def get_distinct_vals(session, field):
    cur = session.cursor()
    cur.execute("select distinct {} from dam".format(field))
    vals = cur.fetchall()
    return [val[0] for val in vals]


# get all logs in this session with their associated Castor String and last line number read
def get_logs(session):
    cur = session.cursor()
    cur.execute("select log_name, castor_string, last_line from logs")
    vals = cur.fetchall()
    return [[val[0], val[1], val[2]] for val in vals]


# check if field contains date strings
def is_date_field(session, field):
    cur = session.cursor()
    cur.execute("select {} from dam limit 1".format(field))
    val = cur.fetchall()
    try:
        valid_datetime = datetime.strptime(val[0][0], "%Y-%m-%d %H:%M:%S.%f")
        return True
    except Exception as e:
        print(e)
        return False


# get all rows in the given date range for a given date field with the appropriate filters
def query_timeline(session, date_field, start_date, end_date, fields, filter_map):
    cur = session.cursor()
    select_string = 'select {},{} from dam'.format(date_field, ",".join(fields))
    time_string = ""
    if start_date != "":
        time_string += ' and {} >= "{}"'.format(date_field, start_date)
    if end_date != "":
        time_string += ' and {} <= "{}"'.format(date_field, end_date)
    filter_string = ""
    for field,filters in filter_map.items():
        or_block = " or ".join(['{}="{}"'.format(field, f) for f in filters])
        filter_string += " and ({})".format(or_block)
    
    query_string = "{} where 1=1{}{} order by {}".format(select_string, time_string, filter_string, date_field)
    print(query_string)
    cur.execute(query_string)
    table_format = "{0}|{1}" + "%s{0}|{1}"*len(cur.description) + "{2}"
    header_format = table_format.format(bcolors.YELLOW, bcolors.ENDC, bcolors.ENDC).replace('|', '!')
    table_format = table_format.format(bcolors.YELLOW, bcolors.BLUE, bcolors.ENDC)
    col_names = [col[0] for col in cur.description]
    header = header_format % tuple(col_names)
    results = cur.fetchall()
    result_index = 0
    for result in results:
        if result_index % 50 == 0:
            print(header)
        fixed_result = ['Null' if val is None else val for val in result]
        print(table_format % tuple(fixed_result))
        result_index += 1


# open a sql shell for the user to type and execute sql queries
def sql_shell(session):
    print("Entering sql shell. Type '\\d' to view table columns. Type '\\q' to quit...")
    cur = session.cursor()
    print("tables:")
    print("dam:  contains the combined log data")
    print("logs: contains log names and their corresponding castor strings")
    while True:
        query = ""
        while ";" not in query:
            query += input("> ") + " "
            if "\\q" in query:
                return
            elif "\\d" in query:
                print("Table logs:")
                logs_cols = get_meta_cols(session)
                for col in logs_cols:
                    print(col)
                print("\nTable dam:")
                dam_cols = get_cols(session)
                for col in dam_cols:
                    print(col)
                print()
                query = ""
        query = query.split(";")[0]
        
        try:
            cur.execute(query)
            table_format = "{0}|{1}" + "%s{0}|{1}"*len(cur.description) + "{2}"
            header_format = table_format.format(bcolors.YELLOW, bcolors.ENDC, bcolors.ENDC).replace('|', '!')
            table_format = table_format.format(bcolors.YELLOW, bcolors.BLUE, bcolors.ENDC)
            col_names = [col[0] for col in cur.description]
            header = header_format % tuple(col_names)
            results = cur.fetchall()
            result_index = 0
            for result in results:
                if result_index % 50 == 0:
                    print(header)
                fixed_result = ['Null' if val is None else val for val in result]
                print(table_format % tuple(fixed_result))
                result_index += 1
        except Exception as e:
            print(e)



