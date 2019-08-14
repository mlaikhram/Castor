# Castor
Command line tool for combining and viewing log files

How to run:
```
python3 castor.py
```

Please read the castor_example.conf for a detailed description on how to create Castor Strings. Castor Strings are needed, because they tell Castor how to parse each line in the given log file. Because of this, Castor can parse any formatted log file as long as the corresponding Castor String is provided.

Usage (Directly from the Castor `help` command)

`list dam` List all available dams

`create dam <dam name>` Create a new dam

`load dam <dam name>` Load an existing dam

`update dam` Update the current dam to reflect any changes to its log files

`list log` List all logs in current dam

`add log <FILE> [FILE]...` Add logs to current dam (FILE may be in wildcard format)

`update log <FILE>`	Update the current dam to reflect any changes to FILE (FILE must be an absolute path)

`create output <FILE>` Create new file to store data output to

`append output <FILE>` Open file to append data output to

`overwrite output <FILE>` Open file to overwrite data output to

`add conf <FILE>` Add conf to current dam (FILE must match exactly)

`fields` Display all fields in current dam

`<field name> values` Display all values stored under field name in current dam

`timeline <date field>` Interactively generate an activity report based on <date field>

`sql` Open sql command line to run sql queries

`quit` Exit Castor
