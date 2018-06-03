#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from main.database.init_db import City, ZipCode
from main.transporter.transporter import Transporter, logger


class CityTransporter(Transporter):

    def map(self, source_content):
        logger.info(source_content)
        entities = []
        for item in source_content:
            logger.info(item)
            target_entity = City()
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
            # zip_code_string = str(item['Postleitzahl'])
            # zip_code_string = zip_code_string.replace('/', ' ')
            # if zip_code_string == ' ':
            #     zip_code_string = 0
            # zip_code = ZipCode()
            # zip_code.zip_code = int(zip_code_string)
            # target_entity.zip_codes.append(zip_code)
            entities.append(target_entity)
        return entities
