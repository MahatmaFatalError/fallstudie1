#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import uuid

class DBHelper:
    def __init__(self, tablename='locations'):
        self.dynamo_db = boto3.resource('dynamodb', region_name='eu-west-1')
        self.table = self.dynamo_db.Table(tablename)

    def create_yelp_location(self, location_json):
        self.table.put_item(
            Item={
                'ID': str(uuid.uuid4()),
                'location': location_json
            }
        )
