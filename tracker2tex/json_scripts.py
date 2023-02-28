import jsbeautifier, json, os


def json_dump(data, directory):
    """Dumps python object to JSON file

    Args:
        data (object): The data object to be dumped 
        directory (_type_): Directory to the JSON dump file
    """
    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    with open(os.path.join(directory), "w", encoding="UTF-8") as f:
        f.write(jsbeautifier.beautify(json.dumps(data), opts))


def json_read(directory:str) -> object:
    """Reads json file. Returns None if the file does not exist

    Args:
        directory (str): Directory to the JSON file

    Returns:
        object: Object in the json file
    """
    if os.path.isfile(directory) == False:
        return(None)
    with open(directory, "r", encoding="UTF-8") as f:
        return(json.load(f))