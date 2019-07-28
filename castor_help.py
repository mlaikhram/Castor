

def dam_help():
    print("list dam\t\t\tList all available dams\n")
    print("create dam <dam name>\t\tCreate a new dam\n")
    print("load dam <dam name>\t\tLoad an existing dam\n")


def log_help():
    print("list log\t\t\tList all logs in current dam\n")
    print("add log <FILE> [FILE]...\tAdd logs to current dam (FILE may be in wildcard format)\n")
    print("delete log <FILE>\t\tDelete log from current dam (FILE must match exactly) [NOT IMPLEMENTED]\n")


def conf_help():
    print("add conf <FILE>\t\t\tAdd conf to current dam (FILE must match exactly) [NOT IMPLEMENTED]\n")


def fields_help():
    print("fields\t\t\t\tDisplay all fields in current dam\n")


def values_help():
    print("<field name> values\t\tDisplay all values stored under field name in current dam\n")


def sql_help():
    print("sql\t\t\t\tOpen sql command line to run sql queries\n")


def quit_help():
    print("quit\t\t\t\tExit Castor\n")


def all_help():
    dam_help()
    log_help()
    conf_help()
    fields_help()
    values_help()
    sql_help()
    quit_help()