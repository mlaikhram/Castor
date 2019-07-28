import parse
import re
import sqlite3
from datetime import datetime
from dam_editor import get_cols, add_cols

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


def rebuild_date(entry_map, date_map):
    rebuilt_map = entry_map
    # print(rebuilt_map)
    for field_name,datetime_format in date_map.items():
        rebuilt_datetime = datetime_format
        components = re.findall(r'%([a-zA-Z])', datetime_format)
        for component in components:
            entry_key = "{}__{}__".format(field_name, component)
            entry_val = entry_map[entry_key]
            # print("entry: {}:{}".format(entry_key, entry_val))
            rebuilt_datetime = rebuilt_datetime.replace("%{}".format(component), entry_val)
            del rebuilt_map[entry_key]
        # print(rebuilt_datetime)
        rebuilt_map[field_name] = rebuilt_datetime
    # print(rebuilt_map)
    return rebuilt_map
            


def add_entry(dam, entry_map, file_name, line_num):
    cur = dam.cursor()
    insert = "insert into dam (log_name, line_number"
    values = " values (?, ?" + ", ?" * len(entry_map) + ")"
    valueArr = [file_name, line_num]
    for field, value in entry_map.items():
        insert += ", {}".format(field)
        valueArr.append(value)
    insert += ")" + values
    # print("insert: " + insert)
    cur.execute(insert, tuple(valueArr))
    dam.commit()


def add_line(dam, line, format_string, date_map, file_name, line_num):
    parsed = parse.parse(format_string, line)
    if parsed is not None:
       entry_map = parsed
       entry_map = rebuild_date(entry_map.named, date_map)
       add_entry(dam, entry_map, file_name, line_num)
    else:
        raise Exception('Could not parse line')


def add_log(dam, log_file, castor_string, starting_line=0):
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
            except Exception as e:
                if line_num - starting_line - parsed_lines == 3:
                    print("Suppressing all future errors in this file")
                if line_num - starting_line - parsed_lines >= 3:
                    continue

                print('Could not parse line {} in {}'.format(line_num, log_file))
                print(line)
                print("Error: {}".format(e))
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




