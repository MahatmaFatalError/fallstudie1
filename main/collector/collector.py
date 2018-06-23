import threading
from abc import ABC, abstractmethod


class Collector(ABC, threading.Thread):

    entity_name = None

    def __init__(self, entity_name):
        super(Collector, self).__init__()
        self.entity_name = entity_name

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _save(self, data):
        pass
