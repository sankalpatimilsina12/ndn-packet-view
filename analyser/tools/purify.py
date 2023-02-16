'''
    Removes dots from JSON file keys exported from Wireshark 
    NDN dissector. MongoDB does not like dots in keys.
    Usage: python purify.py <path_to_json_file>
    Example: python purify.py file.json
    The new file will be saved as new_file.json
'''

import os
import argparse
import json
from settings import LOGGER


class PurifyJSON:
    def __init__(self, file_path):
        self.file_path = file_path

    def _value_resolver(self, pairs):
        dct = {}
        for key, value in pairs:
            if key in dct:
                if type(dct[key]) is list:
                    dct[key].append(value)
                else:
                    dct[key] = [dct[key], value]
            else:
                dct[key] = value
        return dct

    def _remove_dots_from_key(self, data):
        new_data = {}
        for key, value in data.items():
            new_key = key.replace(".", "_")

            if type(value) is dict:
                new_data[new_key] = self._remove_dots_from_key(value)
            elif type(value) is list:
                new_data[new_key] = []
                for item in value:
                    if type(item) is dict:
                        new_data[new_key].append(
                            self._remove_dots_from_key(item))
                    else:
                        new_data[new_key].append(item)
            else:
                new_data[new_key] = value
        return new_data

    def _write_to_file(self, new_data):
        new_file_path = os.path.join(os.path.dirname(
            self.file_path), "new_" + os.path.basename(self.file_path))
        with open(new_file_path, "w") as json_file:
            json.dump(new_data, json_file, indent=2)

    def process_json_file(self):
        with open(self.file_path) as json_file:
            data = json.load(
                json_file, object_pairs_hook=self._value_resolver)

        new_data = []
        for data_item in data:
            new_data.append(self._remove_dots_from_key(data_item))
        self._write_to_file(new_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Remove dots from JSON file keys. MongoDB does not like dots in keys.",
        prog='python -m tools.purify')
    parser.add_argument("file_path", type=str, help="Path to the JSON file")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        LOGGER.error(f"Error: The file {args.file_path} does not exist.")
        exit(1)

    json_purifier = PurifyJSON(args.file_path)
    json_purifier.process_json_file()
