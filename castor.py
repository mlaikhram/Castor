import parse
import re
import sqlite3
from datetime import datetime

# get field names from castor string
def parseForFieldNames(text):
    try:
        field_names = re.findall('{(.+?)}', text)
        return field_names

    except AttributeError:
        raise Exception('castor_string "' + castor_string + '" does not contain any fields')


# reformat castor string to allow the datetimes to be parsed properly
def castorToFormatString(text):
    fields = parseForFieldNames(text)
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


def createSession(session_name, castor_string):
    session = sqlite3.connect(session_name + '.dam')
    cur = session.cursor()
    uncleaned_field_names = parseForFieldNames(castor_string)
    field_names = [field.split('(')[0] for field in uncleaned_field_names]
    print(field_names)
    create_table = "create table dam (log_name, line_number"
    for field in field_names:
        create_table += ", {}".format(field)
    create_table += ")"
    print(create_table)
    cur.execute(create_table)
    return session


def rebuildDate(entry_map, date_map):
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
            


def addEntry(session, entry_map, file_name, line_num):
    cur = session.cursor()
    insert = "insert into dam (log_name, line_number"
    values = " values (?, ?" + ", ?" * len(entry_map) + ")"
    valueArr = [file_name, line_num]
    for field, value in entry_map.items():
        insert += ", {}".format(field)
        valueArr.append(value)
    insert += ")" + values
    # print("insert: " + insert)
    cur.execute(insert, tuple(valueArr))
    session.commit()


def addLine(session, line, format_string, date_map, file_name, line_num):
    parsed = parse.parse(format_string, line)
    if parsed is not None:
       entry_map = parsed
       entry_map = rebuildDate(entry_map.named, date_map)
       addEntry(session, entry_map, file_name, line_num)
    else:
        raise Exception('Could not parse line')


def addLog(session, log_file, format_string, date_map):
    with open(log_file, 'r') as fp:
        print("Adding {} to dam...".format(log_file))
        line = fp.readline()
        line_num = 1
        while line:
            try:
                addLine(session, line, format_string, date_map, log_file, line_num)
            except Exception as e:
                print('Could not parse line {} in {}'.format(line_num, log_file))
                print(line)
                print(e)
            line_num += 1
            line = fp.readline()
        print("Done")


if __name__ == '__main__':

    line = "Jun 23 14:07:38 kali systemd[1]: NetworkManager-dispatcher.service: Succeeded."
    castor_string = "{date(%b %d %H:%M:%S)} {hostname} {service}: {message}"

    # datetime_object = datetime.strptime(line, format_string)
    # print(datetime_object)

    session = createSession('test', castor_string)

    format_string, date_map = castorToFormatString(castor_string)

    print("format_string: " + format_string)
    print("date_map: " + str(date_map))

    addLog(session, 'syslog', format_string, date_map)
    addLog(session, 'auth.log', format_string, date_map)
    addLog(session, 'user.log', format_string, date_map)
    addLog(session, 'daemon.log', format_string, date_map)

    session.close()
