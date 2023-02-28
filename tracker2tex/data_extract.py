import os
from tracker2tex.json_scripts import json_dump
from tracker2tex.num_ops import scinot_to_float
import logging
import itertools


def extract_data(data_path:dir, delimeter:str, file_extension:str, data_dumpsite:dir):
    """Extracts data from folder.

    Args:
        data_path (dir): The root directory to the folder where the data is held
        delimerter (str): The delimeter that separates the datapoints
        file_extension (str): The file extension of the data files
        data_dumpsite (dir): The directory to the JSON file to dump to
    """
    logging.info("Running data extraction")
    logging.debug(f"""    data_path: {data_path}
    delimeter: '{delimeter}'
    file_extension: {file_extension}
    data_dumpsite: {data_dumpsite}""")

    datafiles = []
    for file in os.scandir(data_path):
        if file.name.endswith(file_extension):
            datafiles.append(file.path)
    # datafiles.sort()
    datafiles.reverse()

    # Data parsing
    alldata = {}
    for file in datafiles:
        data = {}
        with open(file, "r", encoding="UTF-8") as f:
            file_lines = f.readlines()

        # Cleans lines
        max_data = 0
        cleaned_data = []
        for line in file_lines:
            
            cleaned_section = [i.replace("\n", "") for i in line.split(delimeter) if i.strip() != ""]       # Splits into separate data sections and remove \n
            if len(cleaned_section) > max_data:
                max_data = len(cleaned_section)

            # Uncertainties
            cleaned_section = [i.split("\\pm") for i in cleaned_section]
            for i, e in enumerate(cleaned_section):
                if i == 0:
                    continue
                if len(e) == 1:
                    cleaned_section[i].append("")
            
            # Remove scientific notation
            for i, datapoint in enumerate(cleaned_section):
                value = scinot_to_float(datapoint[0])
                if value == None:
                    continue
                cleaned_section[i][0] = value
            
            # cleaned_section = [scinot_to_float(i[0]) if scinot_to_float(i[0]) != None else i for i in cleaned_section]    # Converts from scienfic notation to float
            cleaned_data.append(cleaned_section)

        # Data titles
        logging.debug(cleaned_data)
        if len(cleaned_data[0]) == 1:
            try:
                int(cleaned_data[0])
            except:
                if "mass" in "".join(list(itertools.chain.from_iterable([cleaned_data[0]]))):
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
                    logging.warning(f"ERROR EXTRACTING DATA FOR {file}")
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