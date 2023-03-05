import numpy as np
import sigfig
import __main__
import os
import numpy as np
import uncertainties as u

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


def sigdig_rounding(dataframe, digs:int, round_error_values:bool=False, uncertainty_delimeter:str="+/-"):
    """Rounds values 

    Args:
        data (DataFrame): Pandas DataFrame
        digs (int): Number of sigdigs to round to
        round_error_values (bool): Whether to round values with errors'
        uncertainty_delimeter (str): str that deliniates the error
    """     
    for col in dataframe:
        for row in dataframe.index:
            value = dataframe[col][row]
            if str(value) == "nan":
                continue
            if uncertainty_delimeter in str(value):
                if round_error_values == True:
                    dataframe = dataframe.replace(value, "{:.1u}".format(u.ufloat_fromstr("{:.1u}".format(u.ufloat_fromstr(value)))))
                    continue
            rounded_value = np.format_float_positional(float(value), precision=digs, unique=False, fractional=False, trim='k')
            if float(rounded_value) != 0:
                rounded_value = np.format_float_positional(float(str(rounded_value)+"00001"), precision=digs, unique=False, fractional=False, trim='k')
            dataframe = dataframe.replace(value, rounded_value)
    return(dataframe)

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



def remove_dataopints(dataframe, datapoints_to_keep:int):
    """Keeps a defined numer of datapoints from a pandas DataFame

    Args:
        dataframe (DataFrame): pandas DataFrame  to parse
        datapoints_to_keep (int): The total number of datapoints to keep
    """
    indices_to_keep = np.round(np.linspace(0,len(dataframe.index.to_numpy())-1,datapoints_to_keep)).astype(int)
    return(dataframe.iloc[indices_to_keep.tolist()])


def remove_none_set(dataframe) -> dict:
    """Removes all sets of data that contain a "None" element

    Args:
        dataframe (DataFrame): single dataframe dataframe
    """
    indices_to_remove = []
    for key in dataframe:
        for i, item in enumerate(dataframe[key]):
            if item[0] == None:                     
                if i not in indices_to_remove:
                    indices_to_remove.append(i)
    indices_to_remove.sort(reverse=True)
    for i, key in enumerate(dataframe):
        for index in indices_to_remove:
            del dataframe[key][index]

    return(dataframe)
