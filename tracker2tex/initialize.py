import os
import sys
from tracker2tex.json_scripts import json_dump, json_read
from tracker2tex.data_extract import extract_data
from tracker2tex.tui import clear_term
import __main__
import logging

MAIN_ROOT_DIR = os.path.dirname(os.path.realpath(__main__.__file__))


def welcome_script(preferences_json_dir):
    clear_term()
    preferences = {
        "data_directory":"",
        "data_storage_name":"",
    }
    # data_directory
    while True:
        preferences["data_directory"] = input("Enter directory of the data  >").replace("'", "").replace('"', "")
        if os.path.isdir(preferences["data_directory"]) == True:
            break
        clear_term()
        print("Please enter a valid file directory!")

    # data storage name
    preferences["data_storage_name"] = input("Enter name of the data storage file  >")
    if not preferences["data_storage_name"].endswith(".json"):
        preferences["data_storage_name"] = preferences["data_storage_name"] + ".json"

    json_dump(preferences, preferences_json_dir)


def initialize():
    delimeter = " "
    preferences_json_dir = os.path.join(MAIN_ROOT_DIR, "datanalyze_preferences.json")
    
    """Initializes the program -- preferences
    
    Returns:
        Preferences from file
    """
    logging.info("Initializing...")
    preferences = json_read(preferences_json_dir)
    print(preferences_json_dir)
    if preferences == None:
        logging.info("No preferences found--Running welcome script")
        welcome_script(preferences_json_dir)
        sys.exit("Finished program initialization!")
        preferences = json_read(preferences_json_dir)
    extract_data(preferences["data_directory"], delimeter, ".txt", preferences["data_storage_name"])
    return(preferences)


