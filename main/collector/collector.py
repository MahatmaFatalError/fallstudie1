import logging
import threading
from abc import ABC, abstractmethod
from google.api_core.exceptions import ServiceUnavailable
from config import constants
from main.helper.db_helper import SqlHelper, DatastoreHelper

logger = logging.getLogger(__name__)


class Collector(ABC, threading.Thread):
    
    entity_name = None
    test_mode = None
    city_name = None
    zip_codes = []
    current_city = None
    datastore = None

    def __init__(self, entity_name, test_mode):
        super(Collector, self).__init__()

        self.entity_name = entity_name
        self.test_mode = test_mode
        self.datastore = DatastoreHelper()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _create_datastore_entity(self, content) -> dict:
        pass

    def _save(self, entity_id, entity):
        logger.info('Saving {} in Datastore...'.format(self.entity_name))
        result = False

        try:
            self.datastore.create_or_update(self.entity_name, entity_id, entity)
            result = True
        except ServiceUnavailable:
            logger.exception('Service unavailable when trying to save %s', entity_id)
        except:
            logger.exception('An Unknown Error occured')
        return result

    def _fetch_zip_codes_from_database(self):
        sql = SqlHelper(constants.SQL_DATABASE_NAME)

        sql.create_session()
        city_from_db = sql.fetch_city_by_name(self.city_name)
        # get zip codes and close session afterwards
        zip_codes = city_from_db.zip_codes
        sql.close_session()

        for zip in zip_codes:
            self.zip_codes.append(zip.zip_code)

    def _fetch_entities_by_zip_code(self, entity_name):
        result_all = []

        sql = SqlHelper(constants.SQL_DATABASE_NAME)
        sql.create_session()

        for zip_code in self.zip_codes:
            result = sql.fetch_entity_where(class_name=entity_name,
                                            negated=False,
                                            fetch_all=True,
                                            zip_code=str(zip_code))
            result_all += result
        sql.close_session()
        return result_all
