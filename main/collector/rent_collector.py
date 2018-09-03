#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
from main.collector.collector import Collector
from main.helper.result import Result


class RentCollector(Collector):

    filename = None

    def __init__(self, entity_name, test_mode, filepath):
        super(RentCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode
        )
        self.filename = filepath

    def run(self):
        result = Result()
        with open(self.filename, encoding='utf-8') as json_file:
            data = json.load(json_file)
            if not self.test_mode:
                success = self._save_all(data)
                result.set_success(success)
                if not success:
                    result.set_message('Could not save json Data in Google Datastore')
                self.logger.info(result)
        return result

    def _create_datastore_entity(self, content) -> dict:
        target_content = json.dumps(content)
        attributes = {'updatedAt': datetime.datetime.now(), 'content': target_content, 'transported': False}
        return attributes

    def _save_all(self, data):
        success = False
        if 'features' in data:
            features = data['features']
            feature_length = len(features)
            success_count = 0
            for item in features:
                if 'properties' in item:
                    city = item['properties']
                    entity_id = city['schluessel']
                    datastore_entity = self._create_datastore_entity(city)
                    success = self._save(entity_id, datastore_entity)
                    if success:
                        success_count += 1
            if feature_length == success_count:
                success = True
        return success