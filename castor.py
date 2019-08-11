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


# create custom command line prompt to include associated dam
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

# prints a list of all fields in the current dam
def fields_command():
    global dam
    if dam is not None:
        fields = get_cols(dam)
        for field in fields:
            print(field)
    else:
        print("You must create or load a dam in order to check available fields.")


# opens a sql shell to query the dam
def sql_command():
    global dam
    if dam is not None:
        sql_shell(dam)
    else:
        print("You must create or load a dam in order to execute sql queries.")


# reformats dam name to match path to .dam file
def get_dam_format():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dams")
    return path + "/{}.dam"


# get all .dam files (found in dams/)
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
            raw_file_names = [os.path.abspath(path) for path in glob_result if os.path.isfile(path)]
            raw_file_names.sort()
            file_names = []
            old_files = [old_file[0] for old_file in get_logs(dam)]
            for name in raw_file_names:
                if name in old_files:
                    print("{} is already in this dam".format(name))
                else:
                    file_names.append(name)
            if len(raw_file_names) != len(file_names):
                print("Did you mean to update log?")
                print()
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


def timeline_command(comman):
    global dam
    global dam_name
    if dam is None:
        print("You must create or load a dam in order to interact with logs.")
    elif len(command) >= 2:
        if command[1] not in get_cols(dam):
            print("Field: {} is not in this dam.".format(command[1]))
        elif not is_date_field(dam, command[1]):
            print("Field: {} is not a valid datetime field".format(command[1]))
        else:
            start_date = None
            end_date = None
            while start_date == None:
                try:
                    unchecked_date = input("Provide a starting datetime (YYYY-MM-DD HH:MM:SS.SSS) or type 's' to skip: ")
                    if unchecked_date == 's':
                        start_date = ""
                    else:
                        datetime_check = datetime.strptime(unchecked_date, "%Y-%m-%d %H:%M:%S.%f")
                        start_date = unchecked_date
                except Exception:
                    print('{} is not the proper date format (YYYY-MM-DD HH:MM:SS.SSS)'.format(unchecked_date))
                    start_date = None
            while end_date == None:
                try:
                    unchecked_date = input("Provide an ending datetime (YYYY-MM-DD HH:MM:SS.SSS) or type 's' to skip: ")
                    if unchecked_date == 's':
                        end_date = ""
                    else:
                        datetime_check = datetime.strptime(unchecked_date, "%Y-%m-%d %H:%M:%S.%f")
                        end_date = unchecked_date
                        if end_date < start_date:
                            print("Ending datetime cannot be earlier than starting datetime.")
                            end_date = None
                except Exception:
                    print('{} is not the proper date format (YYYY-MM-DD HH:MM:SS.SSS)'.format(unchecked_date))
                    end_date = None
            
            all_cols = get_cols(dam)
            all_cols.remove(command[1])
            print("Available fields:")
            for i in range(len(all_cols)):
                print("[{}] {}".format(i, all_cols[i]))
            chosen_cols = []
            while len(chosen_cols) <= 0:
                try:
                    list_string = input("Please provide a comma separated list of numbers corresponding to the fields you would like to display:\n")
                    list_indices = [int(l_index.strip()) for l_index in list_string.split(',')]
                except Exception:
                    print("{} is not a valid list of indices.".format(list_string))
                    continue
                
                try:
                    chosen_cols = [all_cols[i] for i in list_indices]
                except Exception as e:
                    print(e)
                    chosen_cols.clear()

            filter_map = {}
            while True:
                print("Selected fields:")
                for i in range(len(chosen_cols)):
                    filtered_vals = ""
                    if chosen_cols[i] in filter_map:
                        filtered_vals = " -> {}".format(",".join(filter_map[chosen_cols[i]]))
                    print("[{}] {}{}".format(i, chosen_cols[i], filtered_vals))
                filter_col = ""
                while filter_col == "":
                    try:
                        index_string = input("Please provide a number corresponding to the field you would like to add a filter to or type 'c' to continue: ")
                        if index_string == 'c':
                            break
                        index = int(index_string.strip())
                    except Exception:
                        print("{} is not a valid number.".format(index_string))
                        continue
                    
                    try:
                        filter_col = chosen_cols[index]
                    except Exception as e:
                        print(e)
                        filter_col = ""

                if filter_col == "":
                    break
                field_vals = get_distinct_vals(dam, filter_col)
                if len(field_vals) > 20:
                    while True:
                        yn = input("Display all {} results? (y/n) ".format(len(field_vals))).lower()
                        if yn[0] == "y":
                            break
                        elif yn[0] == "n":
                            field_vals = []
                            break
                if len(field_vals) <= 0:
                    print("No values to display.")
                    continue 
                print("Available values:")
                for i in range(len(field_vals)):
                    print("[{}] {}".format(i, field_vals[i]))
                chosen_vals = []
                while len(chosen_vals) <= 0:
                    try:
                        list_string = input("Please provide a comma separated list of numbers corresponding to the values you would like to track or type 'c' to clear:\n")
                        if list_string == 'c':
                            filter_map.pop(filter_col, None)
                            break
                        list_indices = [int(l_index.strip()) for l_index in list_string.split(',')]
                    except Exception:
                        print("{} is not a valid list of indices.".format(list_string))
                        continue
                    
                    try:
                        chosen_vals = [field_vals[i] for i in list_indices]
                        filter_map[filter_col] = chosen_vals
                    except Exception as e:
                        print(e)
                        chosen_vals.clear()

            query_timeline(dam, command[1], start_date, end_date, chosen_cols, filter_map)
            
    else:
        print("Invalid usage\n")
        timeline_help()


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
    print("      _______________________________________________________________      ")
    print("     (______________________________________________________________()     ")
    print("    (_()  (_____() ______     _____   __(_()   _______   ____    (_()()    ")
    print("   (_()  (_()     (_____()   ( ___() (_____() (______() (___()  (_()()()   ")
    print("  (_()  (_()__   (_()_(_()  (___ ()   (_()   (_()_(_() (_()    (_()()()()  ")
    print(" (_()__(_____()_(_______()_(____()___(_()___(______()_(_()____(_()()()()() ")
    print("(______________________________________________________________()()()()()()")
    print("                               Created by Matthew Laikhram 2019            ")

    print("\nWelcome to Castor! Use in full screen for best experience.")
    print("Type 'help' for a list of commands.\n")
 
    while True:
        raw_command = castor_input().split()
        command = []
        fixed_arg = ""
        for command_arg in raw_command:
            if command_arg[0] == '"' and fixed_arg == "":
                fixed_arg = command_arg
            elif command_arg[-1] == '"':
                fixed_arg += ' ' + command_arg
                command.append(fixed_arg.replace('"', ''))
                fixed_arg = ""
            elif fixed_arg == "":
                command.append(command_arg)
            else:
                fixed_arg += ' ' + command_arg

        if fixed_arg != "":
            print("Error reading input: Invalid double quotes")

        elif len(command) == 0:
            continue
        
        elif command[0] == "quit":
            print("Exiting Castor...")
            if dam is not None:
                dam.close()
            break

        elif command[0] == "help":
            all_help()

        elif command[0] == "fields":
            fields_command()

        elif command[0] == "timeline":
            timeline_command(command)

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
        

