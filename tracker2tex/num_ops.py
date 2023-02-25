import numpy as np
import sigfig
import __main__
import os
import numpy as np
from tracker2tex.tui import user_input, basic_input

MAIN_ROOT_DIR = os.path.dirname(os.path.realpath(__main__.__file__))




def scinot_to_float(num:str) -> float:
    """Converts string in scientific notation from tracker to a float

    Args:
        num (str): The number in scientific notation

    Returns:
        float: Returns the numer. None is returned if the number could not be successfully converted
    """
    try:
        return(float(num.replace("E", "e")))
    except:
        return(None)


def sigdig_rounding(data:dict, digs:int) -> dict:
    for key in data:
        for i, item in enumerate(data[key]):
            if item == None:
                continue
            # Sometimes the trailing zeroes are not included (thanks, numpy <3). The first one rounds it, sometimes not keeping the trailing zeroes.
            # The second round adds 0001 which would not affect the rounding of the number
            data[key][i] = np.format_float_positional(item, precision=digs, unique=False, fractional=False, trim='k')
            if float(data[key][i]) != 0:
                data[key][i] = np.format_float_positional(float(str(data[key][i])+"0001"), precision=digs, unique=False, fractional=False, trim='k')
    return(data)


def float_to_scienfitic(data:dict) -> dict:
    digit = None
    for key in data:
        for i, item in enumerate(data[key]):
            if item == None:
                continue
            digit = str(sigfig.round(item, notation='sci'))
            digit = f"{digit.split('E')[0]}\\cdot 10^{{{digit.split('E')[-1]}}}"
            data[key][i] = digit
    return(data)


def exp_len(datapoint):
    return(len(datapoint.split("10^")[-1].strip("{}")))


def max_exp_len(data):
    max_length = {}
    for key in data:
        running_max_length = 0
        for item in data[key]:
            if item == None:
                continue
            item_exp_len = exp_len(item)
            if running_max_length < item_exp_len:
                running_max_length = item_exp_len
        max_length[key] = running_max_length
    return(max_length)


def parse_data_main(dataset:dict):
    tab = "\t"
    while True:
        match user_input("Select data parsing operation (q to export)", [
            "Remove None Sets",
            "Remove Datapoints",
            "SigDig"
        ], "q"):
                case "Remove None Sets":
                    dataset = remove_none_set(dataset)
                case "Remove Datapoints":
                    number_of_datapoints = len(next(iter(dataset.values())))
                    while True:
                        datapoints_to_keep = basic_input(f"Number of datapoints to keep (max {number_of_datapoints})", int)
                        if datapoints_to_keep <= number_of_datapoints:
                            break
                    dataset = remove_dataopints(dataset, datapoints_to_keep)
                case "SigDig":
                    dataset = sigdig_rounding(dataset, int(basic_input("Number of sigdigs", int)))
                case None:
                    break
    with open(os.path.join(MAIN_ROOT_DIR, input("Export name  >")), "w", encoding="UTF-8") as f:
        for column in dataset:
            f.write(f"{column}{tab}")
        f.write("\n")
        for row in range(len(next(iter(dataset.values())))):
            for column in dataset:
                f.write(str(dataset[column][row]))
                f.write(tab)
            f.write("\n")


def remove_dataopints(dataset, datapoints_to_keep:int):
    indices_to_keep = np.round(np.linspace(0,len(next(iter(dataset.values())))-1,datapoints_to_keep)).astype(int)
    new_dataset = {}
    for key in dataset:
        new_dataset[key] = [dataset[key][i] for i in indices_to_keep]
    return(new_dataset)


def remove_none_set(dataset:dict) -> dict:
    """Removes all sets of data that contain a "None" element

    Args:
        dataset (dict): single dataset dict
    """
    indices_to_remove = []
    for key in dataset:
        for i, item in enumerate(dataset[key]):
            if item == None:
                if i not in indices_to_remove:
                    indices_to_remove.append(i)
    indices_to_remove.sort(reverse=True)
    for i, key in enumerate(dataset):
        for index in indices_to_remove:
            del dataset[key][index]

    return(dataset)
