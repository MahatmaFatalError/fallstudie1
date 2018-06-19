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
    return csv_collector.collect()


def collect_plz():
    plz_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                             constants.CSV,
                                             'german_plz_for_cities',
                                             constants.GCP_ENTITY_PLZ_CITY,
                                             'data/plz_ort.csv',
                                             constants.CSV_DELIMITER_COMMA,
                                             'utf-8',
                                             True)
    return plz_collector.collect()


def collect_restaurants():
    yelp_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR, 'yelp')
    return yelp_collector.collect()


def transport_plz(test_mode=False):
    plz_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                               'plz',
                                               constants.SQL_DATABASE_NAME,
                                               constants.GCP_ENTITY_PLZ_CITY,
                                               constants.SQL_TABLE_CITY,
                                               True)
    return plz_transporter.transport(test_mode)


def transport_cities(test_mode=False):
    csv_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                               'city',
                                               constants.SQL_DATABASE_NAME,
                                               constants.GCP_ENTITY_LOCATION,
                                               constants.SQL_TABLE_CITY,
                                               False)
    return csv_transporter.transport(test_mode)


def transport_restaurants(test_mode=False):
    restaurant_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                               'restaurant',
                                               constants.SQL_DATABASE_NAME,
                                               constants.GCP_ENTITY_RESTAURANT,
                                               constants.SQL_TABLE_RESTAURANT,
                                               False)
    return restaurant_transporter.transport(test_mode)


def collect_kaufkraft():
    yelp_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                              'kaufkraft',
                                              'kaufkraft_for_germany',
                                              constants.GCP_ENTITY_KAUFKRAFT,
                                              'data/kaufkraft.pdf'
                                              )
    return yelp_collector.collect()


if __name__ == '__main__':
    setup_logging()
    # result = collect_plz()
    # result = collect_cities()
    # result = transport_cities(True)
    # result = transport_plz()
    # result = collect_restaurants()
    # result = transport_restaurants()
    result = collect_kaufkraft()
    print(result)
