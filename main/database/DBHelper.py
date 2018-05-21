# -*- coding: utf-8 -*-
from google.cloud import datastore
from pathlib import Path
from config import constants
import logging
import sqlalchemy

logger = logging.getLogger(__name__)


class DatastoreHelper:

    def __init__(self):
        root_path = Path(__file__).parents[2]
        final_path = root_path.joinpath('data/auth/BDCS1.json')
        logger.debug(final_path)
        self.client = datastore.Client.from_service_account_json(final_path)

    def create_or_update(self, entity_name, unique_id, attributes=None):
        key = self.client.key(entity_name, unique_id)
        item = datastore.Entity(key)
        item.update(attributes)
        self.client.put(item)
        return item.key

    def fetch_all_entities(self, entity_name):
        query = self.client.query(kind=entity_name)
        return list(query.fetch())


class SqlHelper:
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

    def insert(self, entry, table_name):
        table = self.meta.tables[table_name]
        statement = table.insert().values(entry)
        self.con.execute(statement)

    def get_table_column_names(self, table_name):
        table = self.meta.tables[table_name]
        table_names = []
        for column in table.c:
            table_names.append(column.key)
        return table_names

    def select_all_entries_where(self, table_name, key, value):
        results = self.meta.tables[table_name]
        statement = results.select().where(getattr(results.c, key) == value)
        return self.con.execute(statement)