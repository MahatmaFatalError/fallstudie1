import logging
import threading
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from config import constants
from main.database.db_helper import DatastoreHelper, SqlHelper
from main.helper.result import Result

logger = logging.getLogger(__name__)


# ... means "not-yet-written code"
# Abstract Transporter Class
class Transporter(ABC, threading.Thread):
    database = None
    source_entity = None
    target_entity = None
    source_db = None
    test_mode = None
    source_entity_id = None

    def __init__(self, database, source_entity, test_mode):
        super(Transporter, self).__init__()
        logger.info('Creating Transporter for Datastore Entity: {0}'
                    .format(source_entity))
        self.database = database
        self.source_entity = source_entity
        self.source_db = DatastoreHelper()
        self.target_db = SqlHelper(self.database)
        self.test_mode = test_mode

    def run(self):
        result = Result()
        logger.info('Starting transport...')
        self.target_db.create_session()
        total = self.source_db.get_total(self.source_entity, only_not_yet_transported=True)
        logger.info('Found a total of %s Entries in Google Datastore', str(total))
        offset = 0
        while offset < total:
            source_entities = self.source_db.fetch_entity(self.source_entity, constants.GCP_FETCH_LIMIT, offset)
            if source_entities:
                for datastore_entity in source_entities:
                    logger.info('Starting mapping...')
                    entities = self.map(datastore_entity)
                    entity_length = len(entities)
                    logger.info('Mapped {0} entities...'.format(str(entity_length)))
                    if not self.test_mode:
                        if entity_length > 0:
                            try:
                                for entity in entities:
                                    if entity:
                                        logger.info('Saving in Database...')
                                        self.target_db.insert(entity)
                                logger.info('Commiting DB entries')
                                self.target_db.commit_session()
                                self.source_db.set_transported(datastore_entity, True)
                                result.set_success(True)
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
                result.set_success(True)
                result.set_message(self.source_entity + ' could not be found in Google Datastore')
            offset += constants.GCP_FETCH_LIMIT
        logger.info(result)

    # maps target and source structure and returns a list of entities to save in db
    @abstractmethod
    def map(self, datastore_entity) -> List:
        pass
