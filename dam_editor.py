import sqlite3
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
            table_format = table_format.format(bcolors.YELLOW, bcolors.BLUE, bcolors.ENDC)
            col_names = [col[0] for col in cur.description]
            header = table_format % tuple(col_names)
            print(header)
            results = cur.fetchall()
            for result in results:
                fixed_result = ['Null' if val is None else val for val in result]
                print(table_format % tuple(fixed_result))
        except Exception as e:
            print(e)



