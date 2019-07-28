def parseConf(conf_file):
    with open(conf_file, 'r') as fp:
        begin_name = None
        castor_string = None
        file_names = []
        line = fp.readline()
        while line:
            strippedLine = line.strip()
            if strippedLine == "" or strippedLine[0] == "#":
                line = fp.readline()
                continue
            
            if line.split()[0] == "BEGIN":
                if begin_name is not None:
                    yield begin_name,castor_string,file_names

                begin_name = line.split()[1]
                castor_string = None
                file_names = []

            elif castor_string is None:
                castor_string = line.replace('\n', "")

            elif strippedLine[0] == "/":
                file_names.append(strippedLine)

            else:
                print("Skipping file: {}\nMust be a valid absolute path".format(strippedLine))

            line = fp.readline()

        yield begin_name,castor_string,file_names

