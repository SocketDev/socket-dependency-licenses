import sys
import csv
import json


class Tools:

    @staticmethod
    def load_json(source):
        try:
            data = json.loads(source)
            is_error = False
        except Exception as error:
            is_error = True
            data = {
                "msg": f"Failed to process JSON data {source}",
                "error": error
            }
        return data, is_error

    @staticmethod
    def write_csv(csv_file: str, column_names: list, data: list):
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            for line in data:
                writer.writerow(line)

    @staticmethod
    def write_json(json_file: str, data: list):
        with open(json_file, 'w', newline='') as file:
            json.dump(data, file)
