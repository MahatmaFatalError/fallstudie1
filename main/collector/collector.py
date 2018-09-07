import logging
import threading
from abc import ABC, abstractmethod
from google.api_core.exceptions import ServiceUnavailable
from config import constants
from main.helper.db_helper import SqlHelper, DatastoreHelper
from main.helper.result import Result


class Collector(ABC, threading.Thread):
    
    entity_name = None
    test_mode = None
    zip_codes = []
    cities = []
    datastore = None
    logger = logging.getLogger(__name__)

    def __init__(self, entity_name, test_mode):
        super(Collector, self).__init__()

        self.entity_name = entity_name
        self.test_mode = test_mode
        self.datastore = DatastoreHelper()

    @abstractmethod
    def run(self) -> Result:
        pass

    @abstractmethod
    def _create_datastore_entity(self, content) -> dict:
        pass

    def _save(self, entity_id, entity):
        self.logger.info('Saving {} in Datastore...'.format(self.entity_name))
        success = False

        try:
            self.datastore.create_or_update(self.entity_name, entity_id, entity)
            success = True
        except ServiceUnavailable:
            self.logger.exception('Service unavailable when trying to save %s', entity_id)
        except:
            self.logger.exception('An Unknown Error occured')
        return success

    def _fetch_zip_codes_from_database(self, delta_handling_attribute):
        sql = SqlHelper(constants.SQL_DATABASE_NAME)

        sql.create_session()

        for city in self.cities:
            city_from_db = sql.fetch_city_by_name(city)
            # get zip codes
            zip_codes = city_from_db.zip_codes
            for zip_code_object in zip_codes:
                collected = getattr(zip_code_object, delta_handling_attribute)
                if not collected:
                    self.zip_codes.append(zip_code_object.zip_code)

        sql.close_session()

    def _fetch_entities_by_zip_code(self, entity_name):
        result_all = []

        sql = SqlHelper(constants.SQL_DATABASE_NAME)
        sql.create_session()

        for zip_code in self.zip_codes:
            kwargs = {'zip_code': str(zip_code)}
            result = sql.fetch_entity_where(class_name=entity_name,
                                            negated=False,
                                            fetch_all=True,
                                            **kwargs)
            result_all += result
        sql.close_session()
        return result_all

