from datetime import datetime

# parse a conf file following conventions described in castor_example.conf
def parseConf(conf_file):
    with open(conf_file, 'r') as fp:
        begin_name = None
        castor_string = None
        file_names = []
        datemaps = {}
        line = fp.readline()
        while line:
            strippedLine = line.strip()
            if strippedLine == "" or strippedLine[0] == "#":
                line = fp.readline()
                continue
            
            if line.split()[0] == "BEGIN":
                if begin_name is not None:
                    yield begin_name,castor_string,file_names,datemaps

                begin_name = line.split()[1]
                castor_string = None
                file_names = []
                datemaps.clear()

            elif castor_string is None:
                castor_string = line.replace('\n', "")

            elif strippedLine[0] == "/":
                file_args = strippedLine.split(",")                
                file_names.append(file_args[0].strip())
                if len(file_args) > 1:
                    datemap = {}
                    for datemap_pair in file_args[1:]:
                        datemap_split = datemap_pair.split(":")
                        try:
                            datemap[datemap_split[0].strip()] = datetime.strptime(datemap_split[1].strip(), "%Y")
                            datemaps[file_args[0]] = datemap
                        except Exception as e:
                            print(e)

            else:
                print("Skipping file: {}\nMust be a valid absolute path".format(strippedLine))

            line = fp.readline()

        yield begin_name,castor_string,file_names,datemaps

