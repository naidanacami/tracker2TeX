import os
from bin.json_scripts import json_dump
from bin.num_ops import scinot_to_float


def extract_data(data_path:dir, delimeter:str, file_extension:str, data_dumpsite:dir):
    """Extracts data from folder.

    Args:
        data_path (dir): The root directory to the folder where the data is held
        delimerter (str): The delimeter that separates the datapoints
        file_extension (str): The file extension of the data files
        data_dumpsite (dir): The directory to the JSON file to dump to
    """

    datafiles = []
    for file in os.scandir(data_path):
        if file.name.endswith(file_extension):
            datafiles.append(file.path)
    # datafiles.sort()
    datafiles.reverse()
    alldata = {}
    for file in datafiles:
        data = {}
        with open(file, "r", encoding="UTF-8") as f:
            file_lines = f.readlines()

        # cleans lines
        max_data = 0
        cleaned_data = []
        for line in file_lines:
            
            cleaned_section = [i.replace("\n", "") for i in line.split(delimeter) if i.strip() != ""]
            if len(cleaned_section) > max_data:
                max_data = len(cleaned_section)
            cleaned_section = [scinot_to_float(i) if scinot_to_float(i) != None else i for i in cleaned_section]
            cleaned_data.append(cleaned_section)

        if len(cleaned_data[0]) == 1:
            try:
                int(cleaned_data[0])
            except:
                del cleaned_data[0]
        # Extracts data
        for data_index in range(max_data):
            data_key = None
            for i, line in enumerate(cleaned_data):
                if i == 0:
                    data_key = line[data_index]
                    data[data_key] = []
                    continue
                elif data_key == None:
                    print("ERROR EXTRACTING DATA FOR {file}")
                    break
                try:
                    data[data_key].append(line[data_index])
                except:
                    data[data_key].append(None)
        alldata[os.path.basename(file)] = data
    json_dump(alldata, data_dumpsite)

if __name__ == "__main__":
    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    extract_data(CURR_DIR, "	", ".txt", os.path.join(CURR_DIR, "data.json"))