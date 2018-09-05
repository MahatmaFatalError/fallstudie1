#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from config import constants
from main.helper import util
from main.helper.db_helper import SqlHelper
from main.helper.signal_handler import SignalHandler
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
    top_how_much = None

    util.setup_logging()

    collect_or_transport = int(input("What do you want to do?\n"
                                     "(1)collect\n"
                                     "(2)transport\n"
                                     "(3)both\n"
                                     "Answer by type in the number."))

    choices = {1: 'city',
               2: 'plz',
               3: 'restaurant',
               4: 'kaufkraft',
               5: 'rent',
               6: 'speisekarte',
               7: 'immoscout',
               8: 'review'}

    action_string = 'What do you want to collect/transport?\n'

    for key in choices.keys():
        choice = '({0}){1}\n'.format(str(key), choices[key])
        action_string += choice

    action_string += "Answer by type in the number."

    action_number = int(input(action_string))

    if action_number in [6, 8, 7]:
        city_or_top = int(input("By City or By Top How Much\n"
                                "(1)By City\n"
                                "(2)By Top How Much\n"
                                "Answer by type in the number."))

        if city_or_top == 1:
            city_name = str(input("For which city?\n"
                                  "Leave Empty for All Cities!"))
            # if you give a city; entities in google datastore must be selectable by "zip_code" Attribute !!!!
            if city_name == '':
                city_name = None
            else:
                check_city(city_name)
        elif city_or_top == 2:
            if collect_or_transport in [1, 3]:
                if action_number in [7, 8]:
                    top_how_much = int(input("Top How Much?\n"
                                             "Answer by type in a number."))

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

        logger.info('Trying to {0} {1} / {2}. Test Mode: {3}'
                    .format(collect_or_transport, collector_method, transporter_method, str(test_mode)))

        try:
            if collect_or_transport == 1 or collect_or_transport == 3:
                collector = getattr(creator, collector_method)(test_mode, city_name, top_how_much)
                if collector:
                    threads.append(collector)
        except AttributeError:
            logger.warning('Collector {0} not found'.format(collector_method))

        try:
            if collect_or_transport == 2 or collect_or_transport == 3:
                transporter = getattr(creator, transporter_method)(test_mode, city_name, top_how_much)
                if transporter:
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
