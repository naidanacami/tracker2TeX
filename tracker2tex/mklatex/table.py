import os
import math
import logging
import __main__
import pandas as pd
import decimal as d
import sigfig as sf
import uncertainties as u
from tracker2tex.tui import user_input, basic_input, clear_term
from tracker2tex.num_ops import sigdig_rounding, float_to_scienfitic, max_exp_len, exp_len, remove_dataopints, remove_none_set


MAIN_ROOT_DIR = os.path.dirname(os.path.realpath(__main__.__file__))


def gentable(table:dict, output_location:dir, center:bool=False):
    """Generates LaTeX table from given dict

    Args:
        table (dict): The tabe in a dicitonary (datapoints)
        output_location (dir): Where to write the table (file will be wiped)
        center (bool): Whether to center the number columns
    """
    tab = " "

    # Table header
    with open(output_location, "w", encoding="UTF-8") as f:
        f.write(f"""\\begin{{table}}[H]
    \\centering
    \\caption{{--Caption Here--}}
    \\label{{--Label Here--}}
""")
        if center == False:
            alignment = "c|"*len(table.keys())
        else:
            alignment = "r|"*len(table.keys())
            column_max_exp_len = max_exp_len(table)
        f.write(f"    \\begin{{tabular}}{{"+alignment.strip("|")+"}\n")

    # Formats the rows and columns (\enspace)
    formatted_table = []
    formatted_column = []
    # For columns titles
    for column in table:
        formatted_column.append(column)
    formatted_table.append(formatted_column)

    # Main dataset handling
    for row in range(len(next(iter(table.values())))):
        formatted_column = []
        for column in table:
            item = table[column][row]
            if item != None:
                if center == True:
                    item = f"${item}" + "\\enskip"*(column_max_exp_len[column] - exp_len(item)) + "$"
                    item = item.replace("\\enskip\\enskip\\enskip\\enskip", "\\qquad").replace("\\enskip\\enskip", "\\quad")
                else:
                    item = f"${item}$"
            else:
                item = f"{item}"
            formatted_column.append(item)
        formatted_table.append(formatted_column)

    # Gets max length of the columns
    max_length = {}
    for ir, row in enumerate(formatted_table):
        for ic, column in enumerate(row):
            if ir == 0:
                max_length[ic] = 0
                continue
            if max_length[ic] < len(column):
                max_length[ic] = len(column)

    # Writes the table body
    with open(output_location, "a", encoding="UTF-8") as f:
        for row in formatted_table:
            for ic, item in enumerate(row):
                tabs_to_add = math.ceil( abs(len(str(item)) - max_length[ic]) )
                logging.debug([ic, len(table.keys())-1])
                last_item = ic == len(table.keys())-1
                if ic != 0 and not last_item:       # Middle elements
                    f.write("    " + f"&    {item}" + tabs_to_add*tab)
                elif ic == 0 and last_item:                         # 1 item table
                    f.write("    " + f"{item}" + tabs_to_add*tab + "    \\\\")
                elif last_item:             # Last element
                    f.write("    " + f"&    {item}" + tabs_to_add*tab + "    \\\\")
                else:
                    f.write("    " + f"{item}" + tabs_to_add*tab)
            f.write("\n")
        f.write(f"""    \end{{tabular}}
\end{{table}}""")


def prettify_uncertainties(dataset:dict, enotation:str, wrap_exponent:bool=False):
    """Turns everythinn into scientific notation

    Args:
        dataset (dict): The dataset
        enotation (str): how to denote "e"
        wrap_exponent (bool): Whether to wrap the exponent in curly braces
    """
    left, right = "", ""
    if wrap_exponent == True:
        left = "{"
        right = "}"
    current_item = 0
    print(f"Prettifying... ({current_item}/?)\r", end="")
    for key in dataset:
        for index, item in enumerate(dataset[key]):
            current_item += 1
            print(f"Prettifying... ({current_item}/?)\r", end="")
            if item == None:
                continue
            uitem = u.ufloat_fromstr(item)
            sci_item = str(sf.round(uitem.nominal_value, notation='sci'))
            nominal_shifted = float(sci_item.split("E")[0])
            exponent = int(sci_item.split("E")[-1])
            uncertainty_shifted = float(d.Decimal(str(uitem.std_dev))*10**(-exponent))                  # Floating point errors occur without decimal library. Convert to string to avoid floating point errors while converting
                                                                                                        # Converted to float after operations to remove trailing zeros
            sigdigs = int(len(str(d.Decimal(str(uncertainty_shifted))).split(".")[-1]))             # Must convert to string before using Decimal or else rounding errors will somehow be introduced
            digit = "(" + format(nominal_shifted, f".{sigdigs}f") + f"\\pm{uncertainty_shifted:f}){enotation}{left}{exponent}{right}"
            dataset[key][index] = digit
    return(dataset)

def table_builder(dataframe, output_location:dir):
    """Table building main

    Args:
        dataframe (DataFrame): Pandas DataFrame
        output_location (dir): Where to write the output
    """
    dataframe = dataframe.where(pd.notnull(dataframe), None)
    table = {}
    column = 0
    used_columns = []
    # User selects columns
    while True:
        column += 1
        user_in = user_input(f"Select column {column}", list(dataframe.columns), "q", used_columns)
        if user_in == None:
            break
        else:
            table[user_in] = list(dataframe[user_in])
        if len(table.keys()) == len(list(dataframe.columns)):
            break
        used_columns.append(user_in)
    clear_term()
    center_columns = False
    if any(any('+/-' in str(s) for s in subList) for subList in table.values()) == True:    # There are uncertainties
        if input("There are uncertainties in this table. Attempt to prettify? [Y/n] ").lower() == "y":
            table = prettify_uncertainties(dataset=table, enotation="\\cdot 10^", wrap_exponent=True)
            if input("Would you like to center the data columns? [Y/n] ").lower() == "y":
                center_columns = True
    else:
        match user_input("Select data format", ["As-is", "SigDig as-is", "SigDig Scientific"]):
            case "As-is":
                pass
            case "SigDig as-is":
                table = sigdig_rounding(table, int(basic_input("Number of sigdigs", int)))
            case "SigDig Scientific":
                table = float_to_scienfitic(sigdig_rounding(table, int(basic_input("Number of sigdigs", int))))  
                if input("Would you like to center the data columns? [Y/n] ").lower() == "y":
                    center_columns = True
    gentable(table=table, output_location=output_location, center=center_columns)
    print(f"\nSuccessfully generated table at:\n{output_location}")

