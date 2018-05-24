from abc import ABC, abstractmethod


# ... means "not-yet-written code"
# Abstract Transporter
class Transporter(ABC):

    def __init__(self, database, source_entity, target_table):
        self.database = database
        self.source_entity = source_entity
        self.target_table = target_table

    @abstractmethod
    def transport(self):
        ...

    # maps target and source structure and return entity to save in db
    @abstractmethod
    def map(self, source_entity, target_entity):
        ...