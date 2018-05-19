from importlib import import_module
from .collector import Collector


def create(collector_name):
    try:
        if '.' in collector_name:
            module_name, class_name = collector_name.rsplit('.', 1)
        else:
            module_name = collector_name
            class_name = collector_name.capitalize()

        collector_module = import_module('.' + module_name, package='collector')

        collector_class = getattr(collector_module, class_name)

        instance = collector_class()

    except (AttributeError, ModuleNotFoundError):
        raise ImportError('{} is not part of our collectors!'.format(collector_name))
    else:
        if not issubclass(collector_class, Collector):
            raise ImportError("We don't have {}".format(collector_class))

    return instance
