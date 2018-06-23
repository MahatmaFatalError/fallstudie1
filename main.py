#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from main.helper.SignalHandler import SignalHandler
from main.helper.creator import Creator
import os
import threading
import json
import logging.config
import logging
import signal

logger = logging.getLogger(__name__)

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


def main():
    setup_logging()
    action_number = int(input("What do you want to collect and transport? (1)city, (2)plz, (3)restaurant, (4)kaufkraft."
                              " Answer by type in the number."))
    test_mode_number = int(input("Execution in test mode?. 1(yes), (2)no."
                                 " Answer by type in the number."))

    action = None
    test_mode = None

    if action_number == 1:
        action = 'city'
    elif action_number == 2:
        action = 'plz'
    elif action_number == 3:
        action = 'restaurant'
    elif action_number == 4:
        action = 'kaufkraft'

    if test_mode_number == 1:
        test_mode = True
    elif test_mode_number == 2:
        test_mode = False

    threads = list()
    stopper = threading.Event()

    if action and test_mode:
        collector_method = 'create_' + action + '_collector'
        transporter_method = 'create_' + action + '_transporter'

        logger.info('Executing {0} and {1}. Test Mode: {2}'
                    .format(collector_method, transporter_method, str(test_mode)))

        creator = Creator()
        collector = getattr(creator,collector_method)()
        transporter = getattr(creator,transporter_method)(test_mode)

        threads.append(collector)
        threads.append(transporter)

        handler = SignalHandler(stopper, threads)
        signal.signal(signal.SIGINT, handler)

        collector.start()
        transporter.start()


if __name__ == '__main__':
    main()



