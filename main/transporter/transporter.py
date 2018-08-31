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
    city_name = None

    def __init__(self, database, source_entity, test_mode, city_name):
        super(Transporter, self).__init__()
        logger.info('Creating Transporter for Datastore Entity: {0}'
                    .format(source_entity))
        self.database = database
        self.source_entity = source_entity
        self.source_db = DatastoreHelper()
        self.target_db = SqlHelper(self.database)
        self.test_mode = test_mode
        self.city_name = city_name

    def run(self):
        results = []
        logger.info('Starting transport...')
        self.target_db.create_session()
        total = self.source_db.get_total(self.source_entity, only_not_yet_transported=True)
        logger.info('Found a total of %s entries in Google Datastore', str(total))
        offset = 0
        while offset < total:
            result = self._transport(offset)
            results.append(result)
            offset += constants.GCP_FETCH_LIMIT
            # i dont know why but google datastore doesn't allow a offset greater than 2500
            if offset == 2500:
                logger.info('Resetting offset...')
                offset = 0
                total = self.source_db.get_total(self.source_entity, only_not_yet_transported=True)
                logger.info('Found a total of %s entries in Google Datastore', str(total))
        for result in results:
            logger.info(result)
        logger.info('Done transporting Restaurants...')

    def _transport(self, offset):
        result = Result()
        limit = constants.GCP_FETCH_LIMIT
        source_entities = self.source_db.fetch_entity(self.source_entity, limit, offset, '=', transported=False)
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
                                    logger.info('Saving in database...')
                                    self.target_db.insert(entity)
                            logger.info('Commiting DB entries')
                            self.target_db.commit_session()
                            result.set_success(True)
                            result.set_message('Fetched entries from offset {0} with limit {1}'
                                               .format(str(offset), str(limit)))
                        except SQLAlchemyError as err:
                            result.set_success(False)
                            result.set_message(err.code)
                            logger.exception('An SQLAlchemyError occured')
                        finally:
                            self.target_db.close_session()
                    else:
                        result.set_success(True)
                        result.set_message('There are no mapped entities that can be saved in database')
                    self.source_db.set_transported(datastore_entity, True)
                else:
                    result.set_success(True)
                    result.set_message('Test Mode active')
            else:
                result.set_success(False)
                result.set_message('No "content" attribute found in entity from Google Datastore')
        else:
            result.set_success(False)
            result.set_message(self.source_entity + ' could not be found in Google Datastore')
        return result

    # maps target and source structure and returns a list of entities to save in db
    @abstractmethod
    def map(self, datastore_entity) -> List:
        pass
