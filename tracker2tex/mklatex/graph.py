import os
import __main__
from tracker2tex.tui import user_input

main_root_dir = os.path.dirname(os.path.realpath(__main__.__file__))


def set_builder(data):
    output_location = os.path.join(main_root_dir, "graph_output.tex")
    dataset = data[user_input("Select which dataset to use:", list(data.keys()))]
    graph = {}

    graph["x"] = dataset[user_input(f"Select x data", list(dataset.keys()))]
    graph["y"] = dataset[user_input(f"Select y data", list(dataset.keys()))]
    
    with open(output_location, "w", encoding="UTF-8") as f:
        for i in range(len(graph["x"])):            # x and y sane len
            if graph["x"][i] == None or graph["y"][i] == None:
                continue
            f.write(f"({graph['x'][i]}, {graph['y'][i]})")