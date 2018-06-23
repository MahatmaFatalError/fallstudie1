#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import logging
from main.collector.collector import Collector
from main.database.db_helper import DatastoreHelper
from main.helper import util
from main.helper.result import Result

logger = logging.getLogger(__name__)


class RentCollector(Collector):

    entity_id = None
    filename = None

    def __init__(self, entity_id, entity_name, compressed, filepath):
        super(RentCollector, self).__init__(
            entity_name=entity_name,
            compressed=compressed
        )
        self.entity_id = entity_id
        self.filename = filepath

    def run(self):
        result = Result()
        with open(self.filename, encoding='utf-8') as json_file:
            data = json.load(json_file)
            success = self._save_all(data)
            result.set_success(success)
        if not success:
            result.set_message('Could not save json Data in Google Datastore')
        logger.info(result)

    def _save_all(self, data):
        success = False
        if 'features' in data:
            features = data['features']
            feature_length = len(features)
            success_count = 0
            for item in features:
                success = self._save(item)
                if success:
                    success_count += 1
            if feature_length == success_count:
                success = True
        return success

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
        logger.debug(target_content)
        attributes = {'updatedAt': datetime.datetime.now(), 'content': target_content, 'transported': False}
        key = db.create_or_update(self.entity_name, self.entity_id, attributes)
        if key:
            success = True
        return success
