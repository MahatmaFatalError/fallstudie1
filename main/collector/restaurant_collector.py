# -*- coding: utf-8 -*-
import datetime
import logging
from main.helper.exception import YelpError
from google.api_core.exceptions import ServiceUnavailable
from config import constants
from main.collector.collector import Collector
from main.database.db_helper import SqlHelper, DatastoreHelper
from urllib.error import HTTPError

from main.helper.yelp import YelpHelper

logger = logging.getLogger(__name__)


class RestaurantCollector(Collector):

    city_name = None

    def __init__(self, entity_name, test_mode, city_name):
        super(RestaurantCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode
        )

        self.location = None
        self.offset = None
        self.current_path = None
        self.city_name = city_name

    def run(self):
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        yelp_helper = YelpHelper()
        db.create_session()
        if self.city_name is None:
            cities = db.fetch_all(constants.SQL_TABLE_CITY)
        else:
            cities = db.fetch_entity_where('City', True, False, name=self.city_name)
        try:
            for city in cities:
                name = city.name
                for zip_code in city.zip_codes:
                    if not zip_code.requested:
                        zip_completed = True
                        self.location = str(zip_code.zip_code) + ', ' + str(name) + ', Deutschland'
                        self.offset = 0
                        content = yelp_helper.get_search(self.location, self.offset)
                        if 'error' not in content and not self.test_mode:
                            total = content['total']
                            save_success = self._save(content)
                            if save_success is False:
                                zip_completed = False
                            logger.info(u'Found {0} Entries...'.format(total))
                            while self.offset < total \
                                    and (self.offset + constants.YELP_SEARCH_LIMIT <= 1000) \
                                    and save_success is True:
                                content = yelp_helper.get_search(self.location, self.offset)
                                self.offset += constants.YELP_SEARCH_LIMIT + 1
                                if 'error' not in content:
                                    save_success = self._save(content)
                                    if save_success is False:
                                        zip_completed = False
                                else:
                                    raise YelpError(content['error']['code'], content['error']['description'])
                        else:
                            raise YelpError(content['error']['code'], content['error']['description'])
                        if zip_completed is True:
                            zip_code.requested = True
                            db.commit_session()
        except HTTPError as error:
            logger.exception('Encountered HTTP error %s on %s:\nAbort program.', error.code, error.url)
        except YelpError as err:
            logger.exception(err)
        finally:
            db.close_session()

    def _save(self, data):
        logger.info('Saving {} in Datastore...'.format(self.entity_name))
        result = False
        db = DatastoreHelper()
        attributes = {'path': self.current_path,
                      'location': self.location,
                      'offset': self.offset,
                      'updated_at': datetime.datetime.now(),
                      'content': data,
                      'transported': False}
        entity_id = str(self.current_path) + str(self.location) + str(self.offset)
        try:
            db.create_or_update(self.entity_name, entity_id, attributes)
            result = True
        except ServiceUnavailable:
            logger.exception('Service unavailable when trying to save %s', entity_id)
        except:
            logger.exception('An Unknown Error occured')
        return result
