#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging

from main.database.init_db import City
from main.helper import util
from main.transporter.transporter import Transporter
from main.database.DBHelper import SqlHelper, DatastoreHelper

logger = logging.getLogger(__name__)


class CsvTransporter(Transporter):

    def transport(self):
        source_db = DatastoreHelper()
        target_db = SqlHelper(self.database)
        source_entities = source_db.fetch_all_entities(self.source_entity)
        target_db_columns = target_db.get_table_column_names(self.target_table)
        logger.debug(target_db_columns)
        for message in source_entities:
            compressed_content = message['content']
            decompresed_content = util.decompress(compressed_content)
            json_string = util.base64_to_string(decompresed_content)
            content = json.loads(json_string)
            entities = self.map(content, City())
            logger.info(entities)
            target_db.create_session()
            target_db.insert_all(entities)

    def map(self, source_entity, target_entity):
        entities = []
        for item in source_entity:
            target_entity = City() # TODO; instantiate dynamic entity
            target_entity.id = item['Lfd. Nr.']
            # split additional "Stadt" Prefix from name cell
            target_entity.name = str(item['Stadt']).split(',')[0]
            pop = str(item['Bevölkerung gesamt'])
            target_entity.population = pop.replace('/', ' ')
            if target_entity.population == ' ':
                target_entity.population = 0
            pop_sqkm = str(item['Bevölkerung je km2'])
            target_entity.population_sqkm = pop_sqkm.replace('/', ' ')
            if target_entity.population_sqkm == ' ':
                target_entity.population_sqkm = 0
            size_sqkm = str(item['Fläche in km'])
            target_entity.size_sqkm = size_sqkm.replace(',', '.').replace('/', '')
            if target_entity.size_sqkm == ' ':
                target_entity.size_sqkm = 0
            zip = str(item['Postleitzahl'])
            target_entity.zip_code = zip.replace('/', ' ')
            if target_entity.zip_code == ' ':
                target_entity.zip_code = 0
            entities.append(target_entity)
        return entities
