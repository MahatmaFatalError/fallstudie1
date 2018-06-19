#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from main.transporter.transporter import Transporter, logger


class KaufkraftTransporter(Transporter):

    def map(self, source_content):
        entities = []
        for item in source_content:
            city_name = item['city']
            # TODO: region landkreis etc entfernen
            # \W = regex for any non word character
            splits = re.compile('\W').split(city_name)
            city_name_for_query = '%'.join(splits)
            city_object_db = self.target_db.fetch_city_by_name(city_name_for_query)
            if city_object_db:
                buying_power = item['buyingpower_2017_euro_a_head']
                city_object_db.buying_power = buying_power
                logger.debug(city_object_db)
            entities.append(city_object_db)
        return entities
