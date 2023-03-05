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


def export_to_csv(dataframe, directory:dir, uncertainty_delimeter:str="\+/-"):
    if directory.endswith(".csv") == False:
        directory = f"{directory}.csv"

    match check_uncertainties(dataframe=dataframe, uncertainty_delimeter="\+/-"):
        case 0: # no uncertainties
            dataframe.to_csv(directory, index=False)
            print(f"Successfully exported to {directory}")
            return

    match user_input(query="Uncertainties detected! Would you like to:", answers=[
        "Keep formatting",
        "Seperate uncertainty into separate column"
]):
            case "Keep formatting":
                pass
            case "Seperate uncertainty into separate column":
                dataframe = seperate_uncertainty(dataframe=dataframe)
    dataframe.to_csv(directory, index=False)
    print(f"Successfully exported to {directory}")