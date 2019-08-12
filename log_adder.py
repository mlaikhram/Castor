import parse
import re
import sqlite3
from datetime import datetime
from dam_editor import get_cols, add_cols

global last_datetime
last_datetime = {}


# get field names from castor string
def parse_for_field_names(text):
    try:
        field_names = re.findall('{(.+?)}', text)
        return field_names

    except AttributeError:
        raise Exception('castor_string "' + castor_string + '" does not contain any fields')


# reformat castor string to allow the datetimes to be parsed properly
def castor_to_format_string(text):
    fields = parse_for_field_names(text)
    reformatted = text
    
    date_field_format = "{}({})"
    date_field_map = {}
    for field_name in fields:
        result = parse.parse(date_field_format, field_name)
        if result is not None:
            date_field_map[result[0]] = result[1]
            generic_date_string = re.sub(r'%([a-zA-Z])', '{' + result[0] + r'__\1__}', result[1])
            reformatted = reformatted.replace('{' + field_name + '}', generic_date_string)

    return reformatted, date_field_map


# rebuild date into proper date format after separating it to properly parse log line
def rebuild_date(entry_map, date_map):
    global last_datetime
    rebuilt_map = entry_map
    for field_name,datetime_format in date_map.items():
        rebuilt_datetime = datetime_format
        components = re.findall(r'%([a-zA-Z])', datetime_format)
        for component in components:
            entry_key = "{}__{}__".format(field_name, component)
            entry_val = entry_map[entry_key]
            rebuilt_datetime = rebuilt_datetime.replace("%{}".format(component), entry_val)
            del rebuilt_map[entry_key]
        reformatted_datetime = datetime.strptime(rebuilt_datetime, datetime_format)
        if reformatted_datetime.year == 1900:
            if field_name in last_datetime:
                reformatted_datetime = reformatted_datetime.replace(year=last_datetime[field_name].year)
                if reformatted_datetime < last_datetime[field_name]:
                    reformatted_datetime = reformatted_datetime.replace(year=reformatted_datetime.year+1)
            else:
                new_year_str = None
                user_prompt = "Date field {} does not have a year! Please provide a starting year: ".format(field_name)
                while new_year_str is None:
                    new_year_str = input(user_prompt)
                    try:
                        new_year = int(new_year_str)
                        if new_year < 1000 or new_year > 9999:
                            raise ValueError
                        reformatted_datetime = reformatted_datetime.replace(year=new_year)
                    except ValueError:
                        new_year_str = None
                        user_prompt = "Please provide a valid year (YYYY): "
        rebuilt_map[field_name] = reformatted_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        last_datetime[field_name] = reformatted_datetime
    return rebuilt_map
            


# insert entry map into the dam
def add_entry(dam, entry_map, file_name, line_num):
    cur = dam.cursor()
    insert = "insert into dam (log_name, line_number"
    values = " values (?, ?" + ", ?" * len(entry_map) + ")"
    valueArr = [file_name, line_num]
    for field, value in entry_map.items():
        insert += ", {}".format(field)
        valueArr.append(value)
    insert += ")" + values
    cur.execute(insert, tuple(valueArr))
    dam.commit()


# convert log file line into an entry map to be inserted into the dam
def add_line(dam, line, format_string, date_map, file_name, line_num):
    parsed = parse.parse(format_string, line)
    if parsed is not None:
       entry_map = parsed
       entry_map = rebuild_date(entry_map.named, date_map)
       add_entry(dam, entry_map, file_name, line_num)
    else:
        raise Exception('Could not parse line')


# add all lines of a log file into the dam table and add log file metadata into the logs table
# starting_line represents the offset to read the file from 
# (in order to allow for reading updated versions of previously added logs)
def add_log(dam, log_file, castor_string, starting_line=0, default_datemap={}):
    global last_datetime
    last_datetime = default_datemap

    format_string, date_map = castor_to_format_string(castor_string)
    old_cols = get_cols(dam)
    current_cols = get_fields_from_castor_string(castor_string)
    new_cols = [col for col in current_cols if col not in old_cols]
    add_cols(dam, new_cols)

    with open(log_file, 'r') as fp:
        if starting_line > 0:
            print("Checking for updates to {}...".format(log_file))
        else:
            print("Adding {} to dam...".format(log_file))

        line = fp.readline()
        line_num = 0
        parsed_lines = 0
        while line:
            if line_num < starting_line:
                line_num += 1
                line = fp.readline()
                continue
            elif starting_line > 0 and line_num == starting_line:
                print("Found new lines!")
            try:
                line_num += 1
                add_line(dam, line, format_string, date_map, log_file, line_num)
                parsed_lines += 1
            except Exception:
                if line_num - starting_line - parsed_lines == 5:
                    print("Suppressing all future errors in this file")
                if line_num - starting_line - parsed_lines >= 5:
                    continue

                print('Could not parse line {} in {}'.format(line_num, log_file))
                print(line)
            line = fp.readline()
        
        if line_num > starting_line or line_num == 0:
            print("Successfully parsed {} of {} lines.".format(parsed_lines, line_num - starting_line))

        if parsed_lines > 0:
            cur = dam.cursor()
            insert_log = "replace into logs(log_name, castor_string, last_line) values (?, ?, ?)"
            cur.execute(insert_log, tuple([log_file, castor_string, line_num]))
            dam.commit()

        elif starting_line > 0 and line_num == starting_line:
            print("{} is already up to date".format(log_file))

        else:
            print("{} was not added".format(log_file))
        last_datetime.clear()


# parse a castor string to get a list of its fields
def get_fields_from_castor_string(castor_string):
    unparsed_fields = castor_string.split('{')[1:]
    unparsed_fields = [field.split('}')[0] for field in unparsed_fields]
    fields = []
    for field in unparsed_fields:
        if '(' in field:
            fields.append(field.split('(')[0])
        else:
            fields.append(field)
    return fields




