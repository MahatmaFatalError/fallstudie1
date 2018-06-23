#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import datetime
import json
import logging
from main.collector.collector import Collector
from main.database.db_helper import DatastoreHelper
from main.helper import util
from main.helper.result import Result

logger = logging.getLogger(__name__)


class CsvCollector(Collector):

    data = []
    filename = None
    delimiter = None
    entity_id = None
    encoding = None

    def __init__(self, entity_id, entity_name, filename, delimiter, encoding=None, compressed=False):
        super(CsvCollector, self).__init__(
            entity_name=entity_name,
            compressed=compressed
        )
        self.entity_id = entity_id
        self.delimiter = delimiter
        self.filename = filename
        self.encoding = encoding

    def run(self):
        result = Result()
        with open(self.filename, encoding=self.encoding) as data:
            csv_reader = csv.DictReader(data, delimiter=self.delimiter)
            column_names = csv_reader.fieldnames
            for row in csv_reader:
                item = {}
                for name in column_names:
                    attribute = row[name]
                    item[name] = attribute
                if item[name] != '':
                    self.data.append(item)
        success = self._save(self.data)
        result.set_success(success)
        if not success:
            result.set_message('Could not save csv Data in Google Datastore')
        logger.info(result)

    def _save(self, data):
        success = False
        db = DatastoreHelper()
        if self.compressed:
            json_content = json.dumps(data)
            base64_content = util.string_to_base64(json_content)
            compressed_content = util.compress(base64_content)
            target_content = compressed_content
        else:
            target_content = json.dumps(data)
        attributes = {'updatedAt': datetime.datetime.now(), 'content': target_content, 'transported': False}
        key = db.create_or_update(self.entity_name, self.entity_id, attributes)
        if key:
            success = True
        return success
