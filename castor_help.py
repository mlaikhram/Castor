# all help strings for displaying usage tips to the user

def dam_help():
    print("list dam\t\t\tList all available dams\n")
    print("create dam <dam name>\t\tCreate a new dam\n")
    print("load dam <dam name>\t\tLoad an existing dam\n")
    print("update dam\t\t\tUpdate the current dam to reflect any changes to its log files\n")


def log_help():
    print("list log\t\t\tList all logs in current dam\n")
    print("add log <FILE> [FILE]...\tAdd logs to current dam (FILE may be in wildcard format)\n")
    print("update log <FILE>\t\tUpdate the current dam to reflect any changes to FILE (FILE must be an absolute path)\n")


def conf_help():
    print("add conf <FILE>\t\t\tAdd conf to current dam (FILE must match exactly)\n")


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
