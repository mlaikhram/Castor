import sqlite3
from castor import bcolors


def create_dam(session_name, field_names):
    session = sqlite3.connect(session_name)
    cur = session.cursor()
    print(field_names)
    create_table = "create table dam (log_name, line_number"
    for field in field_names:
        create_table += ", {}".format(field)
    create_table += ")"
    print(create_table)
    cur.execute(create_table)
    return session


def load_dam(session_name):
    session = sqlite3.connect(session_name)
    return session
    # TODO print metadata about dam


def get_cols(session):
    cur = session.cursor()
    cur.execute("PRAGMA table_info(dam)")
    fields = cur.fetchall()
    return [field[1] for field in fields]


def get_distinct_vals(session, field):
    cur = session.cursor()
    cur.execute("select distinct {} from dam".format(field))
    vals = cur.fetchall()
    return [val[0] for val in vals]


def sql_shell(session):
    print("Entering sql shell. type '\\q' to quit...")
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
        query = query.split(";")[0]
        print(query)
        
        try:
            cur.execute(query)
            table_format = "{0}|{1}" + "%s{0}|{1}"*len(cur.description) + "{2}"
            table_format = table_format.format(bcolors.YELLOW, bcolors.BLUE, bcolors.ENDC)
            col_names = [col[0] for col in cur.description]
            header = table_format % tuple(col_names)
            print(header)
            results = cur.fetchall()
            for result in results:
                print(table_format % result)
        except Exception as e:
            print(e)



