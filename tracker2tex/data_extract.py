import os
from tracker2tex.json_scripts import json_dump
from tracker2tex.num_ops import scinot_to_float
import logging
import re
import itertools
import sys
import pprint
import uncertainties as u
import pandas as pd


# def csv_update(data_path:dir, delimeters:list, data_storage_dir:dir, file_extension:str):
def csv_update(data_path:dir, data_output_dir:str, delimeters:list, file_extension:str):
    """Extracts data from folder.

    Args:
        data_path (dir): The root directory to the folder where the data is held
        delimerter (str): The list of delimeters that separates the datapoints
        file_extension (str): The file extension of the data files
        data_dumpsite (dir): The directory to the JSON file to dump to
    """
    delimeter = "|".join(delimeters)
    logging.info("Running data extraction")
    logging.debug(f"""    data_path: {data_path}
    delimeter: '{delimeter}'
    file_extension: {file_extension}""")

    datafiles = []
    for file in os.scandir(data_path):
        if file.name.endswith(file_extension):
            datafiles.append(file.path)
    datafiles.sort()
    datafiles.reverse()
    
    if os.path.isdir(data_output_dir) == False:
        os.mkdir(data_output_dir)

    number_of_csvs = len(datafiles)
    current_csv = 0
    print(f"Updating csvs... ({current_csv}/{number_of_csvs})\r", end="")
    for file in datafiles:
        
        current_csv += 1
        print(f"Updating csvs... ({current_csv}/{number_of_csvs})\r", end="")
        output_filename = file.split("\\")[-1].split(".")
        output_filename = os.path.join(data_output_dir, "".join(output_filename[:-1]) + ".csv")
        file_dataframe = pd.DataFrame(extract_data(file, delimeter))
        try:
            file_dataframe.to_csv(output_filename, index=False)
        except PermissionError:
            sys.exit("Please close all csv files!")

def extract_data(file:dir, delimeter:list):
    # Data parsing
    data = {}               # data over a single file
    data_titles = []
    cleaned_section = []    # Data over a line
    with open(file, "r", encoding="UTF-8") as f:
        file_lines = f.readlines()

    # Cleans lines
    max_data_sections = 0
    found_datatitles = False

    for line_number, line in enumerate(file_lines):
        # Gets data titles
        if found_datatitles == False:
            if "mass" in line:
                continue
            data_titles = [e.strip() for e in re.split(delimeter, line) if e.strip() != ""]
            max_data_sections = len(data_titles)        # Using data title instead of actually trying to find it so that the None values don't have to be inserted after the fact
            found_datatitles = True
            # Initializing dataset
            for datatitle in data_titles:
                data[datatitle] = []
            continue

        cleaned_section = [i.replace("\n", "").strip() for i in re.split(delimeter, line) if i.strip() != ""]       # Splits into separate data sections and remove \n
        cleaned_section = [i.split("\\pm") for i in cleaned_section]        # Splits the uncertainties
        
        # appends 0 lenth strings to values with no uncertainty
        # converts uncertainties into floats
        for i, e in enumerate(cleaned_section):
            if len(e) == 1:
                cleaned_section[i].append("")
                continue
            try:
                cleaned_section[i][-1] = float(e[-1])
            except ValueError:
                logging.warning("Error reading: %s!\n\t-> Invalid value error for line \"%s \"" %(file.split('\\')[-1], line))
                cleaned_section[i][-1] = ""

        # Converts scientific notation to float, converts to ufloat
        for i, datapoint in enumerate(cleaned_section):
            uncertainty = datapoint[-1]
            if str(uncertainty).strip() == "":
                cleaned_section[i] = scinot_to_float(datapoint[0])          # No uncertainty given
            else:
                cleaned_section[i] = u.ufloat(scinot_to_float(datapoint[0]), uncertainty)

        # Turns None sets into None. Might be roundabout but I'm reusing old code
        cleaned_section = [e if type(e) != list else None for e in cleaned_section]

        # Makes sure that the number of datapoints conforms with the number of data titles
        section_length = len(cleaned_section)
        if section_length < max_data_sections:
            for _ in range(max_data_sections-section_length):
                cleaned_section.append(None)
        elif section_length > max_data_sections:
            cleaned_section = cleaned_section[:max_data_sections]

        for i, datatitle in enumerate(data_titles):
            data[datatitle].append(cleaned_section[i])

    return(data)