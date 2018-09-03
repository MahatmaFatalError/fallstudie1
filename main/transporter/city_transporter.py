#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
from main.database.init_db import City
from main.transporter.transporter import Transporter


class CityTransporter(Transporter):

    def map(self, datastore_entity):
        entities = []
        if 'content' in datastore_entity:
            content = datastore_entity['content']
            try:
                source_content = json.loads(content)
            except TypeError:
                source_content = content
            for item in source_content:
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
                target_entity.updated_at = datetime.datetime.now()
                entities.append(target_entity)
        return entities
