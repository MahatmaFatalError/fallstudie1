from abc import ABCMeta, abstractmethod


class Collector(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def collect(self):
        pass

    @abstractmethod
    def _save(self, data):
        pass
