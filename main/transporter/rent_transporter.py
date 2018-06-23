#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from main.transporter.transporter import Transporter, logger


class RentTransporter(Transporter):

    def map(self, source_content):
        entities = []
        city_name = source_content['GEN']
        # \W = regex for any non word character
        splits = re.compile('\W').split(city_name)
        city_name_for_query = '%'.join(splits)
        city = self.target_db.fetch_city_by_name(city_name_for_query)
        if city:
            rent_avg = source_content['preis']
            city.rent_avg = rent_avg
            entities.append(city)
        return entities

