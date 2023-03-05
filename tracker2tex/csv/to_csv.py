import numpy as np
import uncertainties as u
from tracker2tex.num_ops import check_uncertainties
from tracker2tex.tui import user_input



def seperate_uncertainty(dataframe):
    for column in dataframe:
        column_index = int(dataframe.columns.get_loc(column))
        dataframe.insert(column_index+1, f"u{column}", dataframe[column].astype(str).apply(lambda x: u.ufloat_fromstr(x).std_dev).copy(), True)     # Replaces std deviation values
        dataframe[column] = dataframe[column].astype(str).apply(lambda x: u.ufloat_fromstr(x).nominal_value).copy()             # Replaces nominal values
        bool_index = dataframe[column].isnull()                                                                                 # Index of null values
        dataframe.iloc[list(bool_index[bool_index].index.values), int(dataframe.columns.get_loc(f"u{column}"))] = np.nan        # nan uncertainties is +/- 1. This removes that
    return(dataframe)


def combine_uncertainties(dataframe, uncertainty_delimeter:str="+/-"):
    uncertainty_delimeter = uncertainty_delimeter.replace("\+", "+")
    for column in dataframe:
        ucol = f"u{column}"
        try:
            ucolumn_index = int(dataframe.columns.get_loc(ucol))
            column_index = int(dataframe.columns.get_loc(column))
        except KeyError:
            continue    # No uncertainty column
        bool_index = ~dataframe[column].isnull() 
        dataframe[column] = dataframe.iloc[list(bool_index[bool_index].index.values), [column_index, ucolumn_index]].apply(lambda row: uncertainty_delimeter.join(row.values.astype(str)), axis=1)
        dataframe = dataframe.drop(ucol, axis=1)
    return(dataframe)



def export_to_csv(dataframe, directory:dir, uncertainty_delimeter:str="\+/-"):
    if directory.endswith(".csv") == False:
        directory = f"{directory}.csv"

    match check_uncertainties(dataframe=dataframe, uncertainty_delimeter=uncertainty_delimeter):
        case 0: # no uncertainties conbined with nominal values
            match user_input(query="No ufloats detected! What would you like to do?", answers=[
                "Keep as-is",
                "Combine nominal and uncertainty columns"
            ]):
                case "Keep as-is":
                    pass
                case "Combine nominal and uncertainty columns":
                    dataframe = combine_uncertainties(dataframe=dataframe)
        case _:
            match user_input(query="ufloat ncertainties detected! Would you like to:", answers=[
                "Keep formatting",
                "Seperate uncertainty into separate column"
            ]):
                    case "Keep formatting":
                        pass
                    case "Seperate uncertainty into separate column":
                        dataframe = seperate_uncertainty(dataframe=dataframe)
    dataframe.to_csv(directory, index=False)
    print(f"Successfully exported to {directory}")