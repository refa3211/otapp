import json
import os


class JSONManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_json(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print("File not found. Creating a new file.")
            with open(self.file_path, 'w') as file:
                json.dump({}, file)
            return {}

    def write_json(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_key_value(self, key, value):
        data = self.read_json()
        data[key] = value
        self.write_json(data)
        print(f"Added key '{key}' with value '{value}' to the JSON file.")

    def delete_key_value(self, key):
        data = self.read_json()
        if key in data:
            del data[key]
            self.write_json(data)
            print(f"Deleted key '{key}' from the JSON file.")
        else:
            print(f"Key '{key}' not found in the JSON file.")

