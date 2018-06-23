import json
import logging
import threading
from abc import ABC, abstractmethod
from sqlalchemy.exc import SQLAlchemyError

from config import constants
from main.database.db_helper import DatastoreHelper, SqlHelper
from main.helper import util
from main.helper.result import Result

logger = logging.getLogger(__name__)


# ... means "not-yet-written code"
# Abstract Transporter Class
class Transporter(ABC, threading.Thread):
    database = None
    source_entity = None
    target_entity = None
    compressed = None
    source_db = None
    target_db = None
    test_mode = None

    def __init__(self, database, source_entity, target_table, compressed, test_mode):
        super(Transporter, self).__init__()
        logger.info('Creating Transporter from {0} to {1}'.format(source_entity, target_table))
        self.database = database
        self.source_entity = source_entity
        self.target_table = target_table
        self.compressed = compressed
        self.source_db = DatastoreHelper()
        self.target_db = SqlHelper(self.database)
        self.test_mode = test_mode

    def run(self):
        result = Result()
        logger.info('Starting transport...')
        self.target_db.create_session()
        total = self.source_db.get_total(self.source_entity)
        logger.info('Found a total of %s Entries in Google Datastore', str(total))
        offset = 0
        while offset < total:
            source_entities = self.source_db.fetch_entity(self.source_entity, constants.GCP_FETCH_LIMIT, offset)
            if source_entities:
                for item in source_entities:
                    if 'content' in item:
                        content = item['content']
                        logger.debug(content)
                        if self.compressed:
                            decompresed_content = util.decompress(content)
                            json_string = util.base64_to_string(decompresed_content)
                            target_content = json.loads(json_string)
                        else:
                            try:
                                target_content = json.loads(content)
                            except TypeError:
                                logger.info('Cannot convert to JSON; trying to map "as-is"')
                                target_content = content
                        entities = self.map(target_content)
                        if not self.test_mode:
                            if len(entities) > 0:
                                try:
                                    for entity in entities:
                                        if entity:
                                            self.target_db.insert(entity)
                                    self.target_db.commit_session()
                                    result.set_success(True)
                                    self.source_db.set_transported(item, True)
                                except SQLAlchemyError as err:
                                    result.set_success(False)
                                    result.set_message(err.code)
                                    logger.exception('An SQLAlchemyError occured')
                                finally:
                                    self.target_db.close_session()
                            else:
                                result.set_success(False)
                                result.set_message('There are no mapped entities that can be saved in database')
                    else:
                        result.set_success(False)
                        result.set_message('No "content" attribute found in entity from Google Datastore')
            else:
                result.set_success(False)
                result.set_message(self.source_entity + ' could not be found in Google Datastore')
            offset += constants.GCP_FETCH_LIMIT
        logger.info(result)

    # maps target and source structure and returns a list of entities to save in db
    @abstractmethod
    def map(self, source_content):
        pass
