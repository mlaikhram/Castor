import parse
import re
import sqlite3
import os
from glob import glob
from datetime import datetime
from log_adder import *

castor_string_linux = "{date(%b %d %H:%M:%S)} {hostname} {service}: {message}"

global dam
dam = None
global dam_name 
dam_name = None

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def castor_raw():
    global dam
    global dam_name
    if dam is None:
        return input("{}[Castor]{} ".format(bcolors.OKBLUE, bcolors.ENDC))
    else:
        return input("{}[Castor]{}{}[{}]{} ".format(bcolors.OKBLUE, 
                                                        bcolors.ENDC, 
                                                        bcolors.WARNING, 
                                                        dam_name, 
                                                        bcolors.ENDC))


def dam_commands(command):
    if command[0] == "list":
        print("Here are all of your dam files:")
    
    elif command[0] == "create":
        if len(command) < 3:
            print("You must provide a name of the dam to create.")
        else:
            if dam is not None:
                dam.close()
            create_session(command[2], castor_string_linux)

    elif command[0] == "load":
        if len(command) < 3:
            print("You must provide a name of the dam to load.")
        else:
            print("Loading dam {}...".format(command[2]))

    else:
        print("Invalid usage (show usage here)")


def log_commands(command):
    global dam
    global dam_name
    if dam is None:
        print("You must create or load a dam in order to interact with logs")
    elif command[0] == "list":
        print("Here are all of the log files in this dam:")
    
    elif command[0] == "add":
        if len(command) < 3:
            print("You must provide a log file (or wildcard) to add.")
        else:
            glob_result = glob(command[2], recursive=True)
            file_names = [path for path in glob_result if os.path.isfile(path)]
            for name in file_names:
                print(name)

            print("found {}{}{} {} matching {}.".format(bcolors.FAIL if len(file_names) < 1 else bcolors.OKGREEN,
                                                   len(file_names), 
                                                   bcolors.ENDC,
                                                   "file" if len(file_names) == 1 else "files",
                                                   command[2]))
            if len(file_names) < 1:
                return

            # TODO offer to use a pre-existing castor_string
            print("Please enter a Castor String to format the {}".format("log" if len(file_names) == 1 else "logs"))
            castor_string = castor_raw()
            for name in file_names:
                add_log(dam, name, castor_string)

    elif command[0] == "delete":
        if len(command) < 3:
            print("You must provide a log file to delete.")
        else:
            if dam is not None:
                dam.close()
            create_session(command[2], castor_string_linux)

    else:
        print("Invalid usage (show usage here)")


def create_session(session_name, castor_string):
    # TODO check if dam already exists
    print("creating dam: {}...".format(session_name))
    session = sqlite3.connect(session_name + '.dam')
    cur = session.cursor()
    uncleaned_field_names = parse_for_field_names(castor_string)
    field_names = [field.split('(')[0] for field in uncleaned_field_names]
    print(field_names)
    create_table = "create table dam (log_name, line_number"
    for field in field_names:
        create_table += ", {}".format(field)
    create_table += ")"
    print(create_table)
    cur.execute(create_table)
    global dam
    global dam_name
    dam = session       
    dam_name = session_name
    print("dam successfully created! Try adding some log files with the 'add log' command.")


if __name__ == '__main__':
    os.system('clear')
    print("Welcome to Castor!")
 
    while True:
        command = castor_raw().split()

        if len(command) == 0:
            continue
        
        if command[0] == "quit":
            print("Exiting Castor...")
            if dam is not None:
                dam.close()
            break

        if len(command) > 1 and command[1] == "dam":
            dam_commands(command)

        elif len(command) > 1 and command[1] == "log":
            log_commands(command)

        else:
            print("Not a valid command. Type 'help' for a list of commands.")
        

    # line = "Jun 23 14:07:38 kali systemd[1]: NetworkManager-dispatcher.service: Succeeded."
    # castor_string = "{date(%b %d %H:%M:%S)} {hostname} {service}: {message}"

    # datetime_object = datetime.strptime(line, format_string)
    # print(datetime_object)

    # session = create_session('test', castor_string)

    # format_string, date_map = castor_to_format_string(castor_string)

    # print("format_string: " + format_string)
    # print("date_map: " + str(date_map))

    # add_log(session, 'syslog', format_string, date_map)
    # add_log(session, 'auth.log', format_string, date_map)
    # add_log(session, 'user.log', format_string, date_map)
    # add_log(session, 'daemon.log', format_string, date_map)

    # session.close()
