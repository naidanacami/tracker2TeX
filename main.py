from bin.json_scripts import json_read
from bin.initialize import initialize
from bin.tui import user_input
from bin.mklatex.table import table_builder
from bin.mklatex.graph import set_builder
from bin.num_ops import parse_data_main
print("All binaries successfully imported!")
import os

def main():
    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
    preferences = initialize()
    
    data = json_read(os.path.join(CURR_DIR, preferences["data_storage_name"]))
    match user_input("Select data operation:", [
        "Table",
        "Set",
        "Data Parsing"
    ]):
        case "Table":
            table_builder(data, os.path.join(CURR_DIR, "table_output.tex"))
        case "Set":
            set_builder(data)
        case "Data Parsing":
            parse_data_main(dataset = data[user_input("Select which dataset to use:", list(data.keys()))])




if __name__ == "__main__":
    main()