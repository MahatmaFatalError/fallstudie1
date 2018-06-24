#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from main.transporter.transporter import Transporter


class KaufkraftTransporter(Transporter):

    @staticmethod
    def parse(city_name):
        result_city = ''
        if ' ' in city_name:
            split_city = city_name.split(' ')
            for part in split_city:
                if 'region' not in part.lower() and 'rhein-kreis' not in part.lower():
                    result_city += part
            return result_city
        else:
            return city_name

    def map(self, datastore_entity):
        entities = []
        if 'content' in datastore_entity:
            content = datastore_entity['content']
            try:
                source_content = json.loads(content)
            except TypeError:
                source_content = content
            for item in source_content:
                city_name = item['city']
                # region landkreis etc entfernen
                result_city = KaufkraftTransporter.parse(city_name)
                # \W = regex for any non word character
                splits = re.compile('\W').split(result_city)
                city_name_for_query = '%'.join(splits)
                city_object_db = self.target_db.fetch_city_by_name(city_name_for_query)
                if city_object_db:
                    buying_power = item['buyingpower_2017_euro_a_head']
                    city_object_db.buying_power = buying_power
                entities.append(city_object_db)
        return entities

