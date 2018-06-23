import threading
from abc import ABC, abstractmethod


class Collector(ABC, threading.Thread):

    compressed = None
    entity_name = None

    def __init__(self, entity_name, compressed):
        super(Collector, self).__init__()
        self.entity_name = entity_name
        self.compressed = compressed

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _save(self, data):
        pass
