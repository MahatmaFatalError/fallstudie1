import csv
import json


class CSVReader:

    def __init__(self):
        self.data = {}

    def read(self, filename):
        with open(filename) as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            column_names = csv_reader.fieldnames
            for name in column_names:
                for row in csv_reader:
                    self.data[name] = row[name]

        return json.dumps(self.data, ensure_ascii=False)

