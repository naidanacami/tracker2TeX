import logging 
logging.basicConfig(filename='log.log', filemode='w', encoding='utf-8', level=logging.DEBUG)
from tracker2tex.initialize import initialize
from tracker2tex.tui import user_input, basic_input
from tracker2tex.num_ops import remove_dataopints, sigdig_rounding
from tracker2tex.data_extract import csv_update
from tracker2tex.mklatex.table import table_builder
from tracker2tex.tracker.addu import add_uncertainties
from tracker2tex.csv.to_csv import export_to_csv
import os
import pandas as pd
logging.info("All modules successfully imported!")


def main():
    delimeter = [" ", "\t"]
    pm = "\+/-"
    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    extra_csv_input = os.path.join(CURR_DIR, "additional_csvs.txt")
    preferences = initialize()
    if input("Upadte csv files? [Y/n] ").lower() == "y":
        csv_update(preferences["data_directory"], preferences["data_storage_name"], delimeter, ".txt")

    csvs = []
    if os.path.isfile(extra_csv_input) == False:
        with open(extra_csv_input, "w", encoding="UTF-8") as _:
            pass
    else:
        with open(extra_csv_input, "r", encoding="UTF-8") as f:
            for i, line in enumerate(f):
                filedir = line.strip("\n")
                if filedir.endswith(".csv") and os.path.isdir(filedir):
                    csvs.append(filedir)
                else:
                    logging.warning(f"Extra file input on line {i} is invalid! {filedir}")

    for file in os.scandir(preferences["data_storage_name"]):
        if file.name.endswith(".csv"):
            csvs.append(file.path)

    chosen_dataset = user_input(query="Select which dataframe to use:", answers=csvs, mask=[f.split("\\")[-1] for f in csvs])
    dataframe = pd.DataFrame(pd.read_csv(chosen_dataset))
    while True:
        match user_input(answers=[
            "Remove None Sets",
            "Remove Data",
            "Round Values",
            "Add Uncertainty (Tracker Only)"
        ], escape_char="q", query="""Selected file: {}

Select data parsing operation:""".format(chosen_dataset.split('\\')[-1])):
            case None:
                break
            case "Remove None Sets":
                dataframe = dataframe.dropna()
            case "Remove Data":
                number_of_datapoints = dataframe.shape[0]
                while True:
                    datapoints_to_keep = basic_input(f"Number of datapoints to keep (max {number_of_datapoints})", int)
                    if datapoints_to_keep <= number_of_datapoints:
                        break
                dataframe = remove_dataopints(dataframe, datapoints_to_keep)
            case "Round Values":
                round_uncertainties = False
                # Implemented before bunction creation. Should be refactored out. Too bad!
                try:    # Only certain values?
                    # True in np.column_stack([dataframe[col].astype(str).str.contains(r"\+/-").any() for col in dataframe])
                    dataframe.astype(float)
                    sigdigs = basic_input("Number of sigdigs", int)
                except ValueError:  # There are uncertainties
                    if sum([dataframe[c].astype(str).str.contains(pm).sum() for c in dataframe]) != dataframe.count().sum():    # Only uncertainties?
                        sigdigs = basic_input("Number of sigdigs", int)
                    if input("Round values with undertainties to uncertainty? [Y/n] ").lower() == "y":
                        round_uncertainties = True
                dataframe = sigdig_rounding(dataframe=dataframe, digs=sigdigs, round_error_values=round_uncertainties)
            case "Add Uncertainty (Tracker Only)":
                sigdigs = basic_input("Significant digit where uncertainty should be added: (Usually 7 for Tracker)", int)
                dataframe = add_uncertainties(dataframe=dataframe, sigdigs=sigdigs)

    match user_input(answers=[
                "Table",
                "Export to CSV"
    ], query="""Select thing:"""):
        case "Table":
            table_builder(dataframe, basic_input(prompt="Output Filename  >", anstype=str))
        case "Export to CSV":
            export_to_csv(dataframe=dataframe, directory=os.path.join(CURR_DIR, basic_input(prompt="Export name", anstype=str)))

if __name__ == "__main__":
    main()