#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging
import re
from main.database.init_db import ZipCode
from main.transporter.transporter import Transporter
from collections import defaultdict

logger = logging.getLogger(__name__)


class PlzTransporter(Transporter):

    def map(self, source_content):
        logger.info('Starting PLZ mapping...')
        # create dictionary with city in key and a list of zip codes as value
        entities = []
        cities = defaultdict(list)
        for row in source_content:
            zip_code = row['plz']
            city_string = row['ort']
            cities[city_string].append(zip_code)
        # loop through cities dictionary and create database entities
        for key in cities:
            splits = re.compile('\W').split(str(key))
            city_name_for_query = '%'.join(splits)
            target_city = self.target_db.fetch_city_by_name(city_name_for_query)
            # create zip code objects
            if target_city is not None: # if city was found in db
                zip_codes = cities[key]
                for item in zip_codes:
                    zip_code = ZipCode()
                    zip_code.zip_code = item
                    zip_code.requested = False
                    zip_code.updated_at = datetime.datetime.now()
                    target_city.zip_codes.append(zip_code)
                logger.info('Found {0} zip codes for {1}'.format(len(target_city.zip_codes), target_city.name))
                entities.append(target_city)
        logger.info('Found {0} cities with zip codes'.format(len(entities)))
        return entities
