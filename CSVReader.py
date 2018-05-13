import csv


class CSVReader:

    def __init__(self):
        self.data = []

    def read(self, filename):
        with open(filename) as data:
            csv_reader = csv.DictReader(data, delimiter=';')
            column_names = csv_reader.fieldnames
            for row in csv_reader:
                item = {}
                for name in column_names:
                    attribute = row[name]
                    item[name] = attribute
                self.data.append(item)

    def get_data(self):
        return self.data