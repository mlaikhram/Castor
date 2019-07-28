import parse
import re
import os
from glob import glob
from datetime import datetime
from castor_help import *
from log_adder import *
from dam_editor import *
from castor_conf_parser import *


global dam
dam = None
global dam_name 
dam_name = None

class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def castor_input():
    global dam
    global dam_name
    if dam is None:
        return input("{}[Castor]{} ".format(bcolors.BLUE, bcolors.ENDC))
    else:
        return input("{}[Castor]{}{}[{}]{} ".format(bcolors.BLUE, 
                                                        bcolors.ENDC, 
                                                        bcolors.YELLOW, 
                                                        dam_name, 
                                                        bcolors.ENDC))


def fields_command():
    global dam
    if dam is not None:
        fields = get_cols(dam)
        for field in fields:
            print(field)
    else:
        print("You must create or load a dam in order to check available fields.")


def sql_command():
    global dam
    if dam is not None:
        sql_shell(dam)
    else:
        print("You must create or load a dam in order to execute sql queries.")


def get_dam_format():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dams")
    return path + "/{}.dam"


def get_dams():
    dam_format = get_dam_format()
    abs_dams = glob(dam_format.format("*"))
    dams = [parse.parse(dam_format, a_dam)[0] for a_dam in abs_dams]
    dams.sort()
    return dams


def dam_commands(command):
    global dam
    global dam_name
    if command[0] == "list":
        dams = get_dams()
        for a_dam in dams:
            print(a_dam)
        print("Found {}{}{} dam {}.".format(bcolors.RED if len(dams) < 1 else bcolors.GREEN,
                                               len(dams), 
                                               bcolors.ENDC,
                                               "file" if len(dams) == 1 else "files"))
    
    elif command[0] == "create":
        if len(command) < 3:
            print("You must provide a name of the dam to create.")
        elif command[2] in get_dams():
            print("Dam: {} already exists. Did you mean to load dam?".format(command[2]))
        else:
            if dam is not None:
                dam.close()
                dam = None
                dam_name = None
            print("Creating dam: {}...".format(command[2]))
            dam = create_dam(get_dam_format().format(command[2]))
            if dam is not None:
                dam_name = command[2]
                print("Dam successfully created! Try adding some log files with the 'add log' command.")

    elif command[0] == "load":
        if len(command) < 3:
            print("You must provide a name of the dam to load.")
        else:
            if command[2] not in get_dams():
                print("Could not find dam: {}. Did you mean to create dam?".format(command[2]))
            else:
                if dam is not None:
                    dam.close()
                    dam = None
                    dam_name = None
                print("Loading dam: {}...".format(command[2]))
                dam = load_dam(get_dam_format().format(command[2]))
                if dam is not None:
                    dam_name = command[2]
                    print("Dam successfully loaded! Available fields:")
                    fields = get_cols(dam)
                    for field in fields:
                        print(field)
    
    elif command[0] == "update":
        logs = get_logs(dam)
        for log in logs:
            try:
                add_log(dam, log[0], log[1], starting_line=int(log[2]))
            except Exception:
                print("Could not find log file: {}".format(log[0]))
            print()
        print("Finished updating dam")

    else:
        print("Invalid usage\n")
        dam_help()


def log_commands(command):
    global dam
    global dam_name
    if dam is None:
        print("You must create or load a dam in order to interact with logs.")
    elif command[0] == "list":
        logs = get_logs(dam)
        for log in logs:
             print("up to line {} in {}".format(log[2], log[0]))
    
    elif command[0] == "add":
        if len(command) < 3:
            print("You must provide a log file (or wildcard) to add.")
        else:
            glob_result = []
            for pattern in command[2:]:
                glob_result += glob(pattern, recursive=True)
            file_names = [os.path.abspath(path) for path in glob_result if os.path.isfile(path)]
            file_names.sort()
            for name in file_names:
                print(name)

            print("Found {}{}{} {}.\n".format(bcolors.RED if len(file_names) < 1 else bcolors.GREEN,
                                                   len(file_names), 
                                                   bcolors.ENDC,
                                                   "file" if len(file_names) == 1 else "files"))
            if len(file_names) < 1:
                return
            
            prev_strings = get_castor_strings(dam)
            if len(prev_strings) > 0:
                print("Castor Strings previously used in this dam:")
                for prev_string in prev_strings:
                    print(prev_string)
                print()
            castor_string = input("Please enter a Castor String to format the {} or type 'q' to cancel\n".format("log" if len(file_names) == 1 else "logs"))
            if castor_string.strip() == "q":
                return
            for name in file_names:
                add_log(dam, name, castor_string)

    elif command[0] == "update":
        if len(command) < 3:
            print("You must provide a log file to update.")
        else:
            logs = get_logs(dam)
            log_names = [log[0] for log in logs]
            if command[2] not in log_names:
                print("{} is not a part of this dam. Did you mean to add log?".format(command[2]))
            else:
                for log in logs:
                    if log[0] == command[2]:
                        add_log(dam, log[0], log[1], starting_line=int(log[2]))

    else:
        print("Invalid usage\n")
        log_help()


def conf_commands(command):
    global dam
    global dam_name
    if dam is None:
        print("You must create or load a dam in order to interact with logs.")
    elif command[0] == "add":
        if len(command) < 3:
            print("You must provide a conf file to add")
        else:
            try:
                for begin_name,castor_string,file_names in parseConf(command[2]):
                    print("adding {} files with Castor String:\n{}\n".format(begin_name, castor_string))
                    for name in file_names:
                        try:
                            add_log(dam, name, castor_string)
                        except Exception as e:
                            print("Could not add file {}".format(name))
                            print(e)
                    print()
                print("Finished reading {}".format(command[2]))
            except Exception:
                print("Could not find file: {}".format(command[2]))
    else:
        print("Invalid usage\n")
        conf_help()


def values_command(command):
    global dam
    if dam is None:
        print("You must create or load a dam in order to check field values.")
    elif command[0] in get_cols(dam):
        values = get_distinct_vals(dam, command[0])
        if len(values) > 20:
            while True:
                yn = input("Display all {} results? (y/n) ".format(len(values))).lower()
                if yn[0] == "y":
                    break
                elif yn[0] == "n":
                    values = []
                    break
        for value in values:
            print(value)
    else:
        print("Field: {} does not exist".format(command[0]))



if __name__ == '__main__':
    os.system('clear')
    print("Welcome to Castor!")
    print("Type 'help' for a list of commands.")
 
    while True:
        command = castor_input().split()

        if len(command) == 0:
            continue
        
        if command[0] == "quit":
            print("Exiting Castor...")
            if dam is not None:
                dam.close()
            break

        if command[0] == "help":
            all_help()

        elif command[0] == "fields":
            fields_command()

        elif command[0] == "sql":
            sql_command()

        elif len(command) > 1 and command[1] == "dam":
            dam_commands(command)

        elif len(command) > 1 and command[1] == "log":
            log_commands(command)

        elif len(command) > 1 and command[1] == "conf":
            conf_commands(command)

        elif len(command) > 1 and command[1] == "values":
            values_command(command)

        else:
            print("Not a valid command. Type 'help' for a list of commands.")
        

