""" util.py """

import json

def read_json(file: str) -> str:
    with open(file, "r") as read_file:
        data = json.load(read_file)
    return data

def write_json(file: str, data: dict) -> None:
    with open(file, "w") as write_file:
        json.dump(data, write_file)
