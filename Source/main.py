# Viet lai ham load map nha Tin. Dung LIST nhe
import json
import os

def load_map(file_path: str):
    # Đường dẫn đến thư mục hiên tại
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Kết hợp đường dẫn thư mục với tên tệp
    file_path = os.path.join(dir_path, file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)

    maps = []
    for map_data in raw_data:
        map_array = map_data["data"]
        maps.append(map_array)

    return maps
