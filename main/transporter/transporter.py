import json
from abc import ABC, abstractmethod
from main.database.DBHelper import DatastoreHelper, logger, SqlHelper
from main.helper import util


# ... means "not-yet-written code"
# Abstract Transporter Class
class Transporter(ABC):
    database = None
    source_entity = None
    target_entity = None
    compressed = None
    source_db = None
    target_db = None

    def __init__(self, database, source_entity, target_table, compressed):
        logger.info('Creating Transporter from {0} to {1}'.format(source_entity, target_table))
        self.database = database
        self.source_entity = source_entity
        self.target_table = target_table
        self.compressed = compressed
        self.source_db = DatastoreHelper()
        self.target_db = SqlHelper(self.database)

    def transport(self, test_mode=False):
        logger.info('Starting transport...')
        self.target_db.create_session()
        source_entities = self.source_db.fetch_all_entities(self.source_entity)
        target_db_columns = self.target_db.get_table_column_names(self.target_table)
        logger.debug(target_db_columns)
        for message in source_entities:
            content = message['content']
            if self.compressed:
                decompresed_content = util.decompress(content)
                json_string = util.base64_to_string(decompresed_content)
                target_content = json.loads(json_string)
            else:
                target_content = json.loads(content)
            entities = self.map(target_content)
            if not test_mode:
                self.target_db.insert_all(entities)
                self.target_db.commit_session()
                self.target_db.close_session()

    # maps target and source structure and returns a list of entities to save in db
    @abstractmethod
    def map(self, source_content):
        ...
