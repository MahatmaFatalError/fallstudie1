#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from google.cloud import datastore
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from config import constants
from main.database.init_db import City, Restaurant
import logging
import sqlalchemy

logger = logging.getLogger(__name__)


class DatastoreHelper:

    def __init__(self):
        root_path = Path(__file__).parents[2]
        final_path = root_path.joinpath('data/auth/BDCS1.json')
        self.client = datastore.Client.from_service_account_json(final_path)

    def create_or_update(self, entity_name, unique_id, attributes=None):
        key = self.client.key(entity_name, unique_id)
        # create key and exclude from index because indexed properties cant be longer than 1500 bytes
        item = datastore.Entity(key, exclude_from_indexes=['content'])
        item.update(attributes)
        self.client.put(item)
        return item.key

    def fetch_entity(self, entity_name, limit, offset):
        logger.info('Fetching from Offset: %s with Limit: %s', str(offset), str(limit))
        query = self.client.query(kind=entity_name)
        result = list(query.fetch(limit=limit, offset=offset))
        return result

    def set_transported(self, entity, value):
        entity['transported'] = value
        self.client.put(entity)

    def get_total(self, entity_name):
        query = self.client.query(kind=entity_name)
        query.keys_only()
        return len(list(query.fetch()))


class SqlHelper:
    con = None
    meta = None
    session = None

    def __init__(self, database):
        self.connect(constants.SQL_DATABASE_USER, constants.SQL_DATABASE_PW, database)

    def connect(self, user, password, db, host=constants.SQL_DATABASE_HOST, port=constants.SQL_DATABASE_PORT):
        # We connect with the help of the PostgreSQL URL
        # connection string found here https://cloud.google.com/appengine/docs/flexible/python/using-cloud-sql-postgres
        url = 'postgresql://{}:{}@{}:{}/{}'
        url = url.format(user, password, host, port, db)
        # url = 'postgresql+psycopg2://{}:{}@/{}?host=/cloudsql/ace-ripsaw-200308:europe-west1:t3am-thd' # for AppEngine
        logger.debug(url)
        # The return value of create_engine() is our connection object
        self.con = sqlalchemy.create_engine(url, client_encoding='utf8')

        # We then bind the connection to MetaData()
        self.meta = sqlalchemy.MetaData(bind=self.con, reflect=True)

    def get_connection(self):
        return self.con

    def create_session(self):
        # create a configured "Session" class
        Session = sessionmaker(bind=self.con)
        # create a Session
        self.session = Session()

    def insert(self, entity):
        merged_entity = self.session.merge(entity)
        id = merged_entity.id
        return id

    def fetch_restaurant_by_id(self, id):
        result = self.session.query(Restaurant). \
            filter(Restaurant.id == id ). \
            first()
        return result

    def commit_session(self):
        self.session.commit()

    def close_session(self):
        self.session.close()

    def insert_all(self, entries):
        self.session.add_all(entries)

    def get_table_column_names(self, table_name):
        table = self.meta.tables[table_name]
        table_names = []
        for column in table.c:
            table_names.append(column.key)
        return table_names

    def fetch_all(self, entity_name):
        result = None
        if entity_name == 'city':
            result = self.session.query(City)
        elif entity_name == 'restaurant':
            result = self.session.query(Restaurant)
        return result

    def fetch_city_by_name(self, name):
        result = self.session.query(City).\
            filter(City.name.like(name)).\
            first()
        return result

