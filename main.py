#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from main.helper import util
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
    action = None
    test_mode = None
    transporter = None
    collector = None

    util.setup_logging()
    action_number = int(input("What do you want to collect and transport?"
                              "(1)city,"
                              "(2)plz,"
                              "(3)restaurant,"
                              "(4)kaufkraft,"
                              "{5}rent."
                              " Answer by type in the number."))
    test_mode_number = int(input("Execution in test mode?. 1(yes), (2)no."
                                 " Answer by type in the number."))

    if action_number == 1:
        action = 'city'
    elif action_number == 2:
        action = 'plz'
    elif action_number == 3:
        action = 'restaurant'
    elif action_number == 4:
        action = 'kaufkraft'
    elif action_number == 5:
        action = 'rent'

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
            collector = getattr(creator, collector_method)()
            if collector:
                threads.append(collector)
        except AttributeError:
            logger.warning('Collector {0} not found'.format(collector_method))

        try:
            transporter = getattr(creator, transporter_method)(test_mode)
            if transporter:
                threads.append(transporter)
        except AttributeError:
            logger.warning('Transporter {0} not found'.format(transporter_method))

            number_threads = len(threads)
            if number_threads > 0:
                logger.info('Created {0} new Thread(s)'.format(str(number_threads)))
                handler = SignalHandler(stopper, threads)
                signal.signal(signal.SIGINT, handler)

                if collector is not None:
                    logger.info('Starting {0} collector'.format(action))
                    collector.start()
                if transporter is not None:
                    logger.info('Starting {0} transporter'.format(action))
                    transporter.start()


if __name__ == '__main__':
    main()



