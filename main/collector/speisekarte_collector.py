# -*- coding: utf-8 -*-
import datetime
from google.api_core.exceptions import ServiceUnavailable
from config import constants
from main.collector.collector import Collector
from main.helper.db_helper import SqlHelper
from urllib.error import HTTPError
from main.helper.jessy_spider import SpeisekarteSpider


class SpeisekarteCollector(Collector):

    city_name = None
    current_city = None
    top_how_much = None

    def __init__(self, entity_name, test_mode, city_name, top_how_much):
        super(SpeisekarteCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode
        )
        self.city_name = city_name
        self.top_how_much = top_how_much

    def run(self):
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        db.create_session()
        if self.city_name is None:
            cities = db.fetch_all(constants.SQL_TABLE_CITY)
        else:
            cities = db.fetch_entity_where('City', True, False, name=self.city_name)
        all_results = []
        try:
            for city in cities:
                self.current_city = city.name
                result = {
                    'city': self.current_city,
                    'total': None,
                    'restaurants': []
                }
                spider = SpeisekarteSpider(self.current_city)
                spider.run()
                spider_result = spider.get_result()
                success = spider_result.get_success()
                if success and not self.test_mode:
                    data = spider_result.get_data()
                    restaurants = data['restaurants']
                    total = data['total']
                    result['total'] = total
                    for restaurant in restaurants:
                        restaurant_id = restaurant['id']
                        entity_id = self.current_city + '$' + restaurant_id
                        datastore_entity = self._create_datastore_entity(restaurant)
                        success = self._save(entity_id, datastore_entity)
                        restaurant_result = {
                            'success': success,
                            'content': restaurant_id
                        }
                        result['restaurants'].append(restaurant_result)
                all_results.append(result)
            self.logger.info(all_results)
        except HTTPError as error:
            self.logger.exception('Encountered HTTP error %s on %s:\nAbort program.', error.code, error.url)
        except:
            self.logger.exception('Something went wrong')
        finally:
            db.close_session()

    def _create_datastore_entity(self, content) -> dict:
        zip_code = content['address']['zip_code']
        attributes = {"updatedAt": datetime.datetime.now(),
                      "zip_code": zip_code,
                      "content": content,
                      "transported": False}
        return attributes
