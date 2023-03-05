import uncertainties as u
import pandas as pd
import sigfig as sf
import logging
import sys
logging.basicConfig(filename='log.log', filemode='w', encoding='utf-8', level=logging.DEBUG)


def add_uncertainties(dataframe, sigdigs:int):
    """Adds uncertainties to tracker values
    Args:
        dataframe (DataFrame): Pandas dataframe
        sigdigs (int): The sigdig where the uncertainty should be added
    """
    current_value = 0
    total_values = dataframe.count().sum()
    print(f"Adding uncertainties... ({current_value}/{total_values})\r", end="")
    for col in dataframe:
        for row in dataframe.index:
            current_value += 1
            value = dataframe[col][row]
            if str(value) == "nan" or "+/-" in str(value):          # Whether uncertainty is already there or if there are duplicate values that got replaced previously.
                continue
            try:
                sci_value = sf.round(value, notation='sci')
            except:
                logging.warning(f"{col}\t{row}\t{value}")
                sys.exit()
            uncertainty = (10**(-(sigdigs-1)+int(str(sci_value).split("E")[-1])))
            dataframe = dataframe.replace(value, "{:.1u}".format(u.ufloat(value, uncertainty)))
            print(f"Adding uncertainties... ({current_value}/{total_values})\r", end="")
    return(dataframe)

if __name__ == "__main__":
    dataframe = pd.DataFrame(pd.read_csv(r"A:\\gdrive\\School\\Anarchist'sScripts\\tracker2TeX2\\edata\\pendulumn.csv"))
    print(add_uncertainties(dataframe, 3))
