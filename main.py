#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from config import constants
from main.helper import util
from main.helper.db_helper import SqlHelper
from main.helper.SignalHandler import SignalHandler
from main.helper.creator import Creator
import threading
import logging
import signal

logger = logging.getLogger(__name__)


def main():
    creator = Creator()
    threads = list()
    stopper = threading.Event()
    test_mode = None
    city_name = None

    collect_or_transport = int(input("What do you want to do?\n"
                                     "(1)collect\n"
                                     "(2)transport\n"
                                     "(3)both\n"
                                     "Answer by type in the number."))

    choices = {1: 'city', 2: 'plz', 3: 'restaurant', 4: 'kaufkraft', 5: 'rent', 6: 'speisekarte', 7: 'immoscout'}

    action_string = 'What do you want to collect/transport?\n'

    for key in choices.keys():
        choice = '({0}){1}\n'.format(str(key), choices[key])
        action_string += choice

    action_string += "Answer by type in the number."

    util.setup_logging()

    action_number = int(input(action_string))
    if action_number == 6:
        city_name = str(input("For which city?"))
        # if you give a city; entities in google datastore must be selectable by "zip_code" Attribute !!!!
        check_city(city_name)

    test_mode_number = int(input("Execution in test mode?\n"
                                 "(1)yes\n"
                                 "(2)no\n"
                                 "Answer by type in the number."))

    action = choices[action_number]

    logger.debug(action)

    if test_mode_number == 1:
        test_mode = True
    elif test_mode_number == 2:
        test_mode = False

    if action is not None and test_mode is not None:
        collector_method = 'create_' + action + '_collector'
        transporter_method = 'create_' + action + '_transporter'

        logger.info('Trying to execute {0} and {1}. Test Mode: {2}'
                    .format(collector_method, transporter_method, str(test_mode)))

        try:
            collector = getattr(creator, collector_method)(test_mode, city_name)
            if collector and (collect_or_transport == 1 or collect_or_transport == 3):
                threads.append(collector)
        except AttributeError:
            logger.warning('Collector {0} not found'.format(collector_method))

        try:
            transporter = getattr(creator, transporter_method)(test_mode, city_name)
            if transporter and (collect_or_transport == 2 or collect_or_transport == 3):
                threads.append(transporter)
        except AttributeError:
            logger.warning('Transporter {0} not found'.format(transporter_method))

        number_threads = len(threads)
        logger.info('Created {0} new Thread(s)'.format(str(number_threads)))
        if number_threads > 0:
            handler = SignalHandler(stopper, threads)
            signal.signal(signal.SIGINT, handler)
            for thread in threads:
                thread_name = type(thread).__name__
                logger.info('Starting Thread: {0}'.format(thread_name))
                thread.start()


def check_city(city_name):
    sql = SqlHelper(constants.SQL_DATABASE_NAME)
    sql.create_session()
    city_from_db = sql.fetch_city_by_name(city_name)
    while city_from_db is None:
        city_name = str(input("City {0} not available in database. Try again!".format(city_name)))
        city_from_db = sql.fetch_city_by_name(city_name)

    sql.close_session()
    return city_name


if __name__ == '__main__':
    main()
