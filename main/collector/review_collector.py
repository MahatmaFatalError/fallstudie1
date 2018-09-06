# -*- coding: utf-8 -*-
import datetime
import pandas as pd
from config import constants
from main.collector.collector import Collector
from main.helper.db_helper import SqlHelper
from main.helper.exception import YelpError
from main.helper.result import Result
from main.helper.yelp import YelpHelper


class ReviewCollector(Collector):

    yelp = None
    current_zip_code = None
    current_city = None
    current_restaurant_id = None
    current_locale = None
    top_how_much = None

    def __init__(self, entity_name, test_mode, city_name, top_how_much):
        super(ReviewCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode
        )
        self.current_city = city_name
        self.top_how_much = top_how_much
        self.yelp = YelpHelper()

    def run(self):
        result = Result()
        result.set_success(True)

        if self.current_city:
            self.cities.append(self.current_city)
        elif self.top_how_much:
            self._fetch_top_how_much()

        restaurants = self._fetch_all_restaurants()
        locale_list = ['en_US', 'de_DE']

        while result.get_success():
            for restaurant in restaurants:
                self.current_restaurant_id = restaurant.id
                self.current_zip_code = restaurant.zip_code
                self.current_city = restaurant.city
                for locale in locale_list:
                    self.current_locale = locale
                    yelp_entity, status_code = self.yelp.get_reviews(self.current_restaurant_id, locale)
                    if 'error' not in yelp_entity:
                        reviews = yelp_entity['reviews']
                        if len(reviews) > 0:
                            datastore_entity = self._create_datastore_entity(yelp_entity)
                            entity_id = self.current_city + '@' + \
                                        str(self.current_zip_code) + '.@' + \
                                        str(self.current_restaurant_id) + '@' + \
                                        locale
                            if not self.test_mode:
                                success = self._save(entity_id, datastore_entity)
                                result.set_success(success)
                        else:
                            self.logger.debug('No Reviews found for restaurant {0} in {1}'
                                              .format(restaurant.name, self.current_city))
                    else:
                        message = yelp_entity['error']['description']
                        result.set_success(False)
                        result.set_message(message)
                        raise YelpError(yelp_entity['error']['code'], message)
        else:
            result.set_success(False)
            result.set_message('Failure when saving Review Entity to Datastore')
        return result

    def _fetch_top_how_much(self):
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        db.create_session()
        df = db.fetch_table_as_dataframe('top_cities')
        self.logger.info('Fetching Top {0}'.format(self.top_how_much))
        cities_dataframe = pd.DataFrame(data=df.iloc[:self.top_how_much], columns={'city'})
        self.cities = cities_dataframe['city'].values.tolist()

    def _create_datastore_entity(self, content) -> dict:
        attributes = {'updatedAt': datetime.datetime.now(),
                      'zip_code': str(self.current_zip_code),
                      'city': self.current_city,
                      'content': content,
                      'restaurant_id': self.current_restaurant_id,
                      'locale': self.current_locale,
                      'transported': False}
        return attributes

    def _fetch_all_restaurants(self):
        self._fetch_zip_codes_from_database()
        result = self._fetch_entities_by_zip_code('Restaurant')
        return result
