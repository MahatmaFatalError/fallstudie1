#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.cloud import datastore


class DBHelper:

    def __init__(self):
        self.client = datastore.Client.from_service_account_json('data/auth/Project_THD-513f30ac6360.json')

    def create_city(self, name, population):
        key = self.client.key('City')

        city = datastore.Entity(key)

        city.update({
            'name': name,
            'population': population
        })

        self.client.put(city)

        return city.key

    def create_restaurant(self, alias, name, lat, long):
        key = self.client.key('Restaurant')

        restaurant = datastore.Entity(key)

        restaurant.update({
            'alias': alias,
            'name': name,
            'long': long,
            'lat': lat
        })

        self.client.put(restaurant)

        return restaurant.key

    def list_all_entities(self, entity_name):
        query = self.client.query(kind=entity_name)

        return list(query.fetch())