#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from main.factory import EverythingFactory
from config import constants
import os
import json
import logging.config
import logging


def setup_logging(default_path='config/logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration"""

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def collect_cities():
    csv_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                             constants.CSV,
                                             'german_cities',
                                             constants.GCP_ENTITY_LOCATION,
                                             'data/staedte.csv',
                                             constants.CSV_DELIMITER_SEMI)
    csv_collector.collect()


def collect_plz():
    plz_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                             constants.CSV,
                                             'german_plz_for_cities',
                                             constants.GCP_ENTITY_PLZ_CITY,
                                             'data/plz_ort.csv',
                                             constants.CSV_DELIMITER_COMMA,
                                             'utf-8',
                                             True)
    plz_collector.collect()


def transport_plz(test_mode=False):
    plz_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                               'plz',
                                               constants.SQL_DATABASE_NAME,
                                               constants.GCP_ENTITY_PLZ_CITY,
                                               constants.SQL_TABLE_CITY,
                                               True)
    plz_transporter.transport(test_mode)


def transport_cities(test_mode=False):
    csv_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                               'city',
                                               constants.SQL_DATABASE_NAME,
                                               constants.GCP_ENTITY_LOCATION,
                                               constants.SQL_TABLE_CITY,
                                               False)
    csv_transporter.transport(test_mode)


def collect_restaurants():
    yelp_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR, 'yelp')
    yelp_collector.collect()


if __name__ == '__main__':
    setup_logging()
    # collect_plz()
    # collect_cities()
    # transport_cities()
    transport_plz(test_mode=False)
    # collect_restaurants()