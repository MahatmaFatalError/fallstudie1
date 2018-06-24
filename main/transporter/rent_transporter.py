#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from main.transporter.transporter import Transporter


class RentTransporter(Transporter):

    def map(self, datastore_entity):
        entities = []
        if 'content' in datastore_entity:
            content = datastore_entity['content']
            try:
                source_content = json.loads(content)
            except TypeError:
                source_content = content
            key = 'GEN'
            if key in source_content:
                city_name = source_content[key]
                # \W = regex for any non word character
                splits = re.compile('\W').split(city_name)
                city_name_for_query = '%'.join(splits)
                city = self.target_db.fetch_city_by_name(city_name_for_query)
                if city:
                    key = 'preis'
                    if key in source_content:
                        rent_avg = source_content['preis']
                        city.rent_avg = rent_avg
                        entities.append(city)
        return entities

