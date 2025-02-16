#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from google.cloud import datastore
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from config import constants
import logging
import sqlalchemy
import pandas as pd


class DatastoreHelper:
    logger = logging.getLogger(__name__)

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

    def fetch_entity(self, entity_name, limit, offset, only_keys, operator, **kwargs):
        """
        :param entity_name: name of the entity
        :param limit: limit to fetch from datastore
        :param offset: offset and limit must be supplied together
        :param only_keys: fetch only keys from db
        :param operator: filter operator (=, <, <=, >, >=)
        :param kwargs: filter key and values
        :return: the fetched datatsore entity
        """
        query = self.client.query(kind=entity_name)
        if kwargs is not None and operator is not None:
            for key, value in kwargs.items():
                query.add_filter(key, operator, value)
        if only_keys:
            query.keys_only()
        if limit is not None and offset is not None:
            self.logger.info('Fetching %s from Google Datastore with offset: %s and limit: %s', entity_name,
                             str(offset), str(limit))
            result = list(query.fetch(limit=limit, offset=offset))
        else:
            self.logger.info('Fetching {0} from Google Datastore'.format(entity_name))
            result = list(query.fetch())
        return result

    def set_transported(self, entity, value):
        entity['transported'] = value
        self.client.put(entity)

    def get_total(self, entity_name, only_not_yet_transported):
        """
        DEPRECATED: used fetch_entity() instead
        :param entity_name:
        :param only_not_yet_transported:
        :return:
        """
        query = self.client.query(kind=entity_name)
        if only_not_yet_transported:
            query.add_filter('transported', '=', False)
        query.keys_only()
        return len(list(query.fetch()))


class SqlHelper:
    con = None
    meta = None
    session = None

    logger = logging.getLogger(__name__)

    def __init__(self, database):
        self._connect(constants.SQL_DATABASE_USER, constants.SQL_DATABASE_PW, database)

    def _connect(self, user, password, db, host=constants.SQL_DATABASE_HOST, port=constants.SQL_DATABASE_PORT):
        # We connect with the help of the PostgreSQL URL
        # connection string found here https://cloud.google.com/appengine/docs/flexible/python/using-cloud-sql-postgres
        url = 'postgresql://{}:{}@{}:{}/{}'
        url = url.format(user, password, host, port, db)
        # url = 'postgresql+psycopg2://{}:{}@/{}?host=/cloudsql/ace-ripsaw-200308:europe-west1:t3am-thd' # for AppEngine
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
        try:
            entity_id = merged_entity.id
        except AttributeError:
            try:
                entity_id = merged_entity.restaurant_id
            except AttributeError:
                entity_id = merged_entity.city_id
        return entity_id

    def fetch_restaurant_by_id(self, id):
        """
         deprecated; use fetch_entity_where() instead
        :param id: yelp restaurant id
        :return: restaurant object
        """
        from main.database.init_db import Restaurant
        result = self.session.query(Restaurant). \
            filter(Restaurant.id == id). \
            first()
        return result

    # deprecated; use fetch_entity_where() instead
    def find_restaurant_by_long_lat(self, long, lat):
        from main.database.init_db import Restaurant
        result = self.session.query(Restaurant). \
            filter(Restaurant.longitude == long). \
            filter(Restaurant.latitude == lat).all()
        return result

    # deprecated; use fetch_entity_where() instead
    def delete_restaurant_by_long_lat(self, long, lat):
        from main.database.init_db import Restaurant
        result = self.session.query(Restaurant). \
            filter(Restaurant.longitude == long). \
            filter(Restaurant.latitude == lat). \
            delete()
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

    def fetch_table_as_dataframe(self, table_name):
        self.logger.info('Fetching {0} from PostgreSQL'.format(table_name))
        dataframe = pd.read_sql_table(table_name=table_name, con=self.con)
        return dataframe

    # deprecated; use fetch_entity_where() instead
    def fetch_all(self, entity_name):
        from main.database.init_db import City, Restaurant, TopCities, ZipCode
        result = None
        if entity_name == 'city':
            result = self.session.query(City)
        elif entity_name == 'restaurant':
            result = self.session.query(Restaurant)
        elif entity_name == 'zip_code':
            result = self.session.query(ZipCode)
        elif entity_name == 'top_cities':
            result = self.session.query(TopCities)
        return result

    def fetch_entity_where(self, class_name, fetch_all=True, negated=False, **kwargs):
        self.logger.info('Fetching Enitity {0} from PostgreSQL'.format(class_name))
        mod = __import__('main.database.init_db', fromlist=[class_name])
        entity_class = getattr(mod, class_name)
        query = self.session.query(entity_class)

        if kwargs is not None:
            for key, value in kwargs.items():
                attribute = getattr(entity_class, key)
                if negated:
                    query = query.filter(attribute != value)
                else:
                    query = query.filter(attribute == value)

        if fetch_all:
            result = query.all()
        else:
            result = query.first()
        return result

    def fetch_city_by_name(self, name):
        from main.database.init_db import City
        result = self.session.query(City). \
            filter(City.name.like(name)). \
            first()
        return result

    def update_entity(self, class_name, attribute_to_select, attribute_value, attribute_to_set, value_to_set):
        db_object = self.fetch_entity_where(class_name, False, False, **{attribute_to_select: attribute_value})
        self.logger.debug('Entity to Update: {0}, Attribute to Update: {1} with Value: {2}'
                          .format(db_object, attribute_to_set, value_to_set))
        setattr(db_object, attribute_to_set, value_to_set)
