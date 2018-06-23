import logging
from importlib import import_module
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


# The Abstract Factory
class AbstractFactory(ABCMeta):

    @staticmethod
    @abstractmethod
    def create(package, name):
        pass


# The Concrete Factory
class EverythingFactory(AbstractFactory):
    @staticmethod
    def create(package, name, *args):
        try:
            if '.' in name:
                module_name, class_name = name.rsplit('.', 1)
            else:
                module_name = name + '_' + package
                class_name = name.capitalize() + package.capitalize()
            module = import_module('.' + module_name, package='main.' + package)
            python_class = getattr(module, class_name)
            instance = python_class(*args)
        except (AttributeError, ModuleNotFoundError):
            raise ImportError('{} is not part of {}!'.format(name, package))
        return instance
