import threading
from abc import ABC, abstractmethod


class Collector(ABC, threading.Thread):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _save(self, data):
        pass
