import os
from tracker2tex.json_scripts import json_dump
from tracker2tex.num_ops import scinot_to_float
import logging
import re
import itertools
import sys


def extract_data(data_path:dir, delimeter:list, file_extension:str, data_dumpsite:dir):
    """Extracts data from folder.

    Args:
        data_path (dir): The root directory to the folder where the data is held
        delimerter (str): The delimeter that separates the datapoints
        file_extension (str): The file extension of the data files
        data_dumpsite (dir): The directory to the JSON file to dump to
    """
    delimeter = "|".join(delimeter)
    logging.info("Running data extraction")
    logging.debug(f"""    data_path: {data_path}
    delimeter: '{delimeter}'
    file_extension: {file_extension}
    data_dumpsite: {data_dumpsite}""")

    datafiles = []
    for file in os.scandir(data_path):
        if file.name.endswith(file_extension):
            datafiles.append(file.path)
    datafiles.sort()
    datafiles.reverse()

    # Data parsing
    alldata = {}            # data over all datafiles
    data = {}               # data over a single file
    data_titles = []
    cleaned_section = []    # Data over a line
    cleaned_data = []       # Data over file (could be refactored out )
    for file in datafiles:
        with open(file, "r", encoding="UTF-8") as f:
            file_lines = f.readlines()

        # Cleans lines
        
        
        max_data_sections = 0
        data_titles.clear()
        cleaned_data.clear()
        # cleaned_section.clear()
        found_datatitles = False

        for line in file_lines:
            # Gets data titles
            if found_datatitles == False:
                if "mass" in line:
                    continue
                data_titles = [e.strip() for e in re.split(delimeter, line) if e.strip() != ""]
                max_data_sections = len(data_titles)        # Using data title instead of actually trying to find it so that the None values don't have to be inserted after the fact
                found_datatitles = True
                continue

            cleaned_section = [i.replace("\n", "").strip() for i in re.split(delimeter, line) if i.strip() != ""]       # Splits into separate data sections and remove \n
            cleaned_section = [i.split("\\pm") for i in cleaned_section]        # Splits the uncertainties
            # appends 0 lenth strings to values with no uncertainty
            for i, e in enumerate(cleaned_section):
                if len(e) == 1:
                    cleaned_section[i].append("")
                    continue
                try:
                    cleaned_section[i][-1] = float(e[-1])
                except ValueError:
                    pass        #! sopafjsaofijspaoifjpsoadifjopasjfopasjfposoij VALUEERROR LOG PLSSSS

            # Converts scientific notation to float
            for i, datapoint in enumerate(cleaned_section):
                cleaned_section[i][0] = scinot_to_float(datapoint[0])

            # Makes sure that the number of datapoints conforms with the number of data titles
            section_length = len(cleaned_section)
            if section_length < max_data_sections:
                for _ in range(max_data_sections-section_length):
                    cleaned_section.append([None, ""])
            elif section_length > max_data_sections:
                cleaned_section = cleaned_section[:max_data_sections]
            cleaned_data.append(cleaned_section)
        # Initializing dataset
        for datatitle in data_titles:
            data[datatitle] = []

        for i, datatitle in enumerate(data_titles):
            for data_index in range(len(cleaned_data)):
                data[datatitle].append(cleaned_data[data_index][i])

        alldata[os.path.basename(file)] = data.copy()
        data.clear()
    json_dump(alldata, data_dumpsite)

if __name__ == "__main__":
    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    extract_data(CURR_DIR, "	", ".txt", os.path.join(CURR_DIR, "data.json"))