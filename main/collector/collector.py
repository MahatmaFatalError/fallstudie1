import threading
from abc import ABC, abstractmethod


class Collector(ABC, threading.Thread):

    entity_name = None
    city_name = None
    test_mode = None

    def __init__(self, entity_name, test_mode):
        super(Collector, self).__init__()
        self.entity_name = entity_name
        self.test_mode = test_mode

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _save(self, data):
        pass
