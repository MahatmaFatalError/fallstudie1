import csv
import io
import datetime
import json
import logging
import uuid

from main.collector.collector import Collector
from main.database.DBHelper import DatastoreHelper

logger = logging.getLogger(__name__)


class Csv(Collector):
    data = []
    filename = None

    def __init__(self):
        Collector.__init__(self)

    def collect(self):
        with open(self.filename, 'r') as data:
            csv_reader = csv.DictReader(data, delimiter=';')
            column_names = csv_reader.fieldnames
            for row in csv_reader:
                item = {}
                for name in column_names:
                    attribute = row[name]
                    item[name] = attribute
                self.data.append(item)

    def save(self, entity_name):
        db = DatastoreHelper()
        json_data = json.dumps(self.data)
        attributes = {'updatedAt': datetime.datetime.now(), 'content': json_data}
        db.create_or_update(entity_name, uuid.uuid4(), attributes)

    def get_data(self):
        return self.data

    def set_filename(self, value):
        self.filename = value
