import os
import math
import __main__
from bin.tui import user_input, basic_input
from bin.num_ops import sigdig_rounding, float_to_scienfitic, max_exp_len, exp_len, remove_dataopints, remove_none_set


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
                last_item = ic == len(table.keys())-1
                if ic != 0 and not last_item:
                    f.write("    " + f"&    {item}" + tabs_to_add*tab)
                elif last_item:
                    f.write("    " + f"&    {item}" + tabs_to_add*tab + "    \\\\")
                else:
                    f.write("    " + f"{item}" + tabs_to_add*tab)
            f.write("\n")
        f.write(f"""    \end{{tabular}}
\end{{table}}""")


def table_builder(data, output_location):
    dataset = data[user_input("Select which dataset to use:", list(data.keys()))]
    table = {}

    column = 0
    used_columns = []
    while True:
        column += 1
        user_in = user_input(f"Select column {column}", list(dataset.keys()), "q", used_columns)
        if user_in == None:
            break
        else:
            table[user_in] = dataset[user_in]
        if len(table.keys()) == len(dataset.keys()):
            break
        used_columns.append(user_in)

    while True:
        match user_input("Select data parsing operation", [
            "Remove None Sets",
            "Remove Datapoints",
        ], "q"):
                case "Remove None Sets":
                    table = remove_none_set(table)
                case "Remove Datapoints":
                    number_of_datapoints = len(next(iter(table.values())))
                    while True:
                        datapoints_to_keep = basic_input(f"Number of datapoints to keep (max {number_of_datapoints})", int)
                        if datapoints_to_keep <= number_of_datapoints:
                            break
                    table = remove_dataopints(table, datapoints_to_keep)
                case None:
                    break

    match(user_input("Select data format", ["As-is", "SigDig as-is", "SigDig Scientific"])):
        case "As-is":
            gentable(table, output_location)
        case "SigDig as-is":
            parsed_talbe = sigdig_rounding(table, int(basic_input("Number of sigdigs", int)))
            gentable(parsed_talbe, output_location)
        case "SigDig Scientific":
            parsed_talbe = float_to_scienfitic(sigdig_rounding(table, int(basic_input("Number of sigdigs", int))))
            if input("Would you like to center the data columns? [Y/n] ").lower() == "y":
                gentable(parsed_talbe, output_location, True)
            else:
                gentable(parsed_talbe, output_location)
    print(f"\nSuccessfully generated table at:\n{output_location}")

