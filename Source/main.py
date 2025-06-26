import numpy as np
import json

def load_map(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)

    maps = []
    for map_data in raw_data:
        map_array = np.array(map_data["data"], dtype=int)
        maps.append(map_array)

    return maps
