#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.cloud import datastore


class DBHelper:

    def __init__(self):
        self.client = datastore.Client.from_service_account_json('data/auth/Project_THD-513f30ac6360.json')

    def create_or_update(self, entity_name, unique_id, attributes=None):
        key = self.client.key(entity_name, unique_id)
        item = datastore.Entity(key)
        item.update(attributes)
        self.client.put(item)
        return item.key

    def list_all_entities(self, entity_name):
        query = self.client.query(kind=entity_name)
        return list(query.fetch())