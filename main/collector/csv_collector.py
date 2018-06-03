#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import datetime
import json
import logging
from main.collector.collector import Collector
from main.database.DBHelper import DatastoreHelper
from main.helper import util

logger = logging.getLogger(__name__)


class CsvCollector(Collector):
    data = []
    filename = None
    delimiter = None
    entity_id = None
    entity_name = None
    encoding = None
    compressed = None

    def __init__(self, entity_id, entity_name, filename, delimiter, encoding=None, compressed=False):
        Collector.__init__(self)
        self.delimiter = delimiter
        self.entity_id = entity_id
        self.filename = filename
        self.entity_name = entity_name
        self.encoding = encoding
        self.compressed = compressed

    def collect(self):
        with open(self.filename, encoding=self.encoding) as data:
            csv_reader = csv.DictReader(data, delimiter=self.delimiter)
            column_names = csv_reader.fieldnames
            logger.debug(column_names)
            for row in csv_reader:
                item = {}
                for name in column_names:
                    attribute = row[name]
                    item[name] = attribute
                if item[name] != '':
                    self.data.append(item)
        logger.debug(self.data)
        self._save(self.data)

    def _save(self, data):
        db = DatastoreHelper()
        if self.compressed:
            json_content = json.dumps(data)
            base64_content = util.string_to_base64(json_content)
            compressed_content = util.compress(base64_content)
            target_content = compressed_content
        else:
            target_content = json.dumps(data)
        attributes = {'updatedAt': datetime.datetime.now(), 'content': target_content}
        db.create_or_update(self.entity_name, self.entity_id, attributes)

    def get_data(self):
        return self.data

    def set_filename(self, value):
        self.filename = value
