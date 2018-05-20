from abc import ABCMeta, abstractmethod, abstractproperty


# ... means "not-yet-written code"
# Abstract Transporter
class Transporter(ABCMeta):

    @abstractproperty
    def source_data(self):
        pass

    @abstractproperty
    def target_data(self):
        pass

    @abstractmethod
    def do_mapping(self):
        pass

    @abstractmethod
    def transport(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def save(self):
        pass