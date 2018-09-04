# -*- coding: utf-8 -*-
import datetime
from main.collector.collector import Collector
from main.helper.exception import YelpError
from main.helper.result import Result
from main.helper.yelp import YelpHelper


class ReviewCollector(Collector):

    yelp = None
    current_zip_code = None
    current_restaurant_id = None

    def __init__(self, entity_name, test_mode, city_name):
        super(ReviewCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode
        )
        self.current_city = city_name
        self.yelp = YelpHelper()

    def run(self):
        result = Result()
        result.set_success(True)
        restaurants = self._fetch_all_restaurants_from_city()
        locale_list = ['en_US', 'de_DE']

        while result.get_success():
            for restaurant in restaurants:
                self.current_restaurant_id = restaurant.id
                self.current_zip_code = restaurant.zip_code
                for locale in locale_list:
                    yelp_entity, status_code = self.yelp.get_reviews(self.current_restaurant_id, locale)
                    if 'error' not in yelp_entity:
                        reviews = yelp_entity['reviews']
                        if len(reviews) > 0:
                            datastore_entity = self._create_datastore_entity(yelp_entity)
                            entity_id = self.current_city + '@' + \
                                        str(self.current_zip_code) + '.@' + \
                                        str(self.current_restaurant_id) + '@' + \
                                        locale
                            if self.test_mode is False:
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

    def _create_datastore_entity(self, content) -> dict:
        attributes = {"updatedAt": datetime.datetime.now(),
                      "zip_code": self.current_zip_code,
                      "content": content,
                      'restaurant_id': self.current_restaurant_id,
                      "transported": False}
        return attributes

    def _fetch_all_restaurants_from_city(self):
        self._fetch_zip_codes_from_database()
        result = self._fetch_entities_by_zip_code('Restaurant')
        return result
