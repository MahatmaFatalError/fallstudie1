#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from main.transporter.transporter import Transporter, logger


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

    def map(self, source_content):
        entities = []
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
                logger.debug(city_object_db)
            entities.append(city_object_db)
        return entities

