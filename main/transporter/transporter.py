import logging
import threading
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from config import constants
from main.helper.db_helper import DatastoreHelper, SqlHelper
from main.helper.result import Result


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
    zip_codes = []

    logger = logging.getLogger(__name__)

    def __init__(self, database, source_entity, test_mode, city_name, top_how_much):
        super(Transporter, self).__init__()
        self.logger.info('Creating Transporter for Datastore Entity: {0}'
                         .format(source_entity))
        self.database = database
        self.source_entity = source_entity
        self.source_db = DatastoreHelper()
        self.target_db = SqlHelper(self.database)
        self.test_mode = test_mode
        self.city_name = city_name

        if self.city_name is not None:
            self._fetch_zip_codes_from_database()

    def run(self):
        results = []
        self.logger.info('Starting transport...')
        self.target_db.create_session()
        total = self._get_entities(None, None, True)
        self.logger.info('Found a total of %s entries in Google Datastore', str(total))
        offset = 0
        while offset < total:
            result = self._transport(offset)
            results.append(result)
            offset += constants.GCP_FETCH_LIMIT
            # i dont know why but google datastore doesn't allow a offset greater than 2500
            if offset == 2500:
                self.logger.info('Resetting offset...')
                offset = 0
                total = self._get_entities(None, None, True)
                self.logger.info('Found a total of %s entries in Google Datastore', str(total))
        for result in results:
            self.logger.info(result)
        self.logger.info('Done transporting Restaurants...')

    def _transport(self, offset):
        result = Result()
        limit = constants.GCP_FETCH_LIMIT
        source_entities = self._get_entities(limit, offset, False)
        if source_entities:
            for datastore_entity in source_entities:
                self.logger.info('Starting mapping...')
                entities = self.map(datastore_entity)
                entity_length = len(entities)
                self.logger.info('Mapped {0} entities...'.format(str(entity_length)))
                if not self.test_mode:
                    if entity_length > 0:
                        try:
                            for entity in entities:
                                if entity:
                                    self.logger.info('Saving in database...')
                                    self.target_db.insert(entity)
                            self.logger.info('Commiting DB entries')
                            self.target_db.commit_session()
                            result.set_success(True)
                            result.set_message('Fetched entries from offset {0} with limit {1}'
                                               .format(str(offset), str(limit)))
                        except SQLAlchemyError as err:
                            result.set_success(False)
                            result.set_message(err.code)
                            self.logger.exception('An SQLAlchemyError occured')
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
            result.set_message(self.source_entity + ' could not be found in Google Datastore')
        return result

    def _fetch_zip_codes_from_database(self):
        sql = SqlHelper(constants.SQL_DATABASE_NAME)

        sql.create_session()
        city_from_db = sql.fetch_city_by_name(self.city_name)
        # get zip codes and close session afterwards
        zip_codes = city_from_db.zip_codes
        sql.close_session()

        for zip_code_obj in zip_codes:
            self.zip_codes.append(zip_code_obj.zip_code)

    def _fetch_entities_by_zip_code(self, entity_name, limit, offset, only_keys):
        result_all = []

        for zip_code in self.zip_codes:
            result = self.source_db.fetch_entity(entity_name,
                                                 limit=limit,
                                                 offset=offset,
                                                 only_keys=only_keys,
                                                 operator='=',
                                                 zip_code=zip_code,  # Speisekarte Transporter need string instead int
                                                 transported=False)
            result_all += result
        return result_all

    def _get_entities(self, limit, offset, only_total):
        if self.zip_codes is None:
            content = self.source_db.fetch_entity(self.source_entity, limit, offset, only_total, '=', transported=False)
        else:
            content = self._fetch_entities_by_zip_code(self.source_entity, limit, offset, only_total)

        if only_total:
            result = len(content)
        else:
            result = content

        return result

    # maps target and source structure and returns a list of entities to save in db
    @abstractmethod
    def map(self, datastore_entity) -> List:
        pass
