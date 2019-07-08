import parse
import re
import os
from glob import glob
from datetime import datetime
from log_adder import *
from dam_editor import *

castor_string_linux = "{date(%b %d %H:%M:%S)} {hostname} {service}: {message}"

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
            # temporary code for linux hard coded format
            uncleaned_field_names = parse_for_field_names(castor_string_linux)
            field_names = [field.split('(')[0] for field in uncleaned_field_names]
            # end temporary code
            dam = create_dam(get_dam_format().format(command[2]), field_names)
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

    else:
        print("Invalid usage (show usage here)")


def log_commands(command):
    global dam
    global dam_name
    if dam is None:
        print("You must create or load a dam in order to interact with logs.")
    elif command[0] == "list":
        print("Here are all of the log files in this dam:")
    
    elif command[0] == "add":
        if len(command) < 3:
            print("You must provide a log file (or wildcard) to add.")
        else:
            glob_result = []
            for pattern in command[2:]:
                glob_result += glob(pattern, recursive=True)
            file_names = [path for path in glob_result if os.path.isfile(path)]
            file_names.sort()
            for name in file_names:
                print(name)

            print("Found {}{}{} {}.".format(bcolors.RED if len(file_names) < 1 else bcolors.GREEN,
                                                   len(file_names), 
                                                   bcolors.ENDC,
                                                   "file" if len(file_names) == 1 else "files"))
            if len(file_names) < 1:
                return

            # TODO offer to use a pre-existing castor_string
            print("Please enter a Castor String to format the {}".format("log" if len(file_names) == 1 else "logs"))
            castor_string = castor_input()
            for name in file_names:
                add_log(dam, name, castor_string)

    elif command[0] == "delete":
        if len(command) < 3:
            print("You must provide a log file to delete.")
        else:
            print("to be implemented...")

    else:
        print("Invalid usage (show usage here)")


def values_command(command):
    global dam
    if dam is None:
        print("You must create or load a dam in order to check field values.")
    elif command[0] in get_cols(dam):
        values = get_distinct_vals(dam, command[0])
        for value in values:
            print(value)
    else:
        print("Field: {} does not exist".format(command[0]))



if __name__ == '__main__':
    os.system('clear')
    print("Welcome to Castor!")
 
    while True:
        command = castor_input().split()

        if len(command) == 0:
            continue
        
        if command[0] == "quit":
            print("Exiting Castor...")
            if dam is not None:
                dam.close()
            break

        if command[0] == "fields":
            fields_command()

        elif command[0] == "sql":
            sql_command()

        elif len(command) > 1 and command[1] == "dam":
            dam_commands(command)

        elif len(command) > 1 and command[1] == "log":
            log_commands(command)

        elif len(command) > 1 and command[1] == "values":
            values_command(command)

        else:
            print("Not a valid command. Type 'help' for a list of commands.")
        

    # line = "Jun 23 14:07:38 kali systemd[1]: NetworkManager-dispatcher.service: Succeeded."
    # castor_string = "{date(%b %d %H:%M:%S)} {hostname} {service}: {message}"

    # datetime_object = datetime.strptime(line, format_string)
    # print(datetime_object)

    # session = create_dam('test', castor_string)

    # format_string, date_map = castor_to_format_string(castor_string)

    # print("format_string: " + format_string)
    # print("date_map: " + str(date_map))

    # add_log(session, 'syslog', format_string, date_map)
    # add_log(session, 'auth.log', format_string, date_map)
    # add_log(session, 'user.log', format_string, date_map)
    # add_log(session, 'daemon.log', format_string, date_map)

    # session.close()
