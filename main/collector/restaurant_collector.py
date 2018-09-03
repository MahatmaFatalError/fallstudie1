# -*- coding: utf-8 -*-
import datetime
from main.helper.exception import YelpError
from config import constants
from main.collector.collector import Collector
from main.helper.db_helper import SqlHelper
from urllib.error import HTTPError

from main.helper.yelp import YelpHelper


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
                            entity_id = str(self.current_path) + str(self.location) + str(self.offset)
                            datastore_entity = self._create_datastore_entity(content)
                            save_success = self._save(entity_id, datastore_entity)
                            if save_success is False:
                                zip_completed = False
                            self.logger.info(u'Found {0} Entries...'.format(total))
                            while self.offset < total \
                                    and (self.offset + constants.YELP_SEARCH_LIMIT <= 1000) \
                                    and save_success is True:
                                content = yelp_helper.get_search(self.location, self.offset)
                                self.offset += constants.YELP_SEARCH_LIMIT + 1
                                if 'error' not in content:
                                    entity_id = str(self.current_path) + str(self.location) + str(self.offset)
                                    datastore_entity = self._create_datastore_entity(content)
                                    save_success = self._save(entity_id, datastore_entity)
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
            self.logger.exception('Encountered HTTP error %s on %s:\nAbort program.', error.code, error.url)
        except YelpError as err:
            self.logger.exception(err)
        finally:
            db.close_session()

    def _create_datastore_entity(self, content) -> dict:
        attributes = {'path': self.current_path,
                      'location': self.location,
                      'offset': self.offset,
                      'updated_at': datetime.datetime.now(),
                      'content': content,
                      'transported': False}
        return attributes
