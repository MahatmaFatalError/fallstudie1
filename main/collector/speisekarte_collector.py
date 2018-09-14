# -*- coding: utf-8 -*-
import datetime
import pandas as pd
from config import constants
from main.collector.collector import Collector
from main.helper.db_helper import SqlHelper
from urllib.error import HTTPError
from main.helper.web_scraper import SpeisekarteSpider


class SpeisekarteCollector(Collector):

    city_name = None
    current_city = None
    current_state = None
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

        if self.top_how_much is not None:
            df = db.fetch_table_as_dataframe('top_cities')
            cities_dataframe = pd.DataFrame(data=df.iloc[:self.top_how_much], columns={'city', 'state'})
            cities = cities_dataframe.values.tolist()
            print(cities)
        elif self.city_name is None:
            city_objects = db.fetch_entity_where('TopCities')
            cities = [[city.state, city.city] for city in city_objects]
        else:
            city_objects = db.fetch_entity_where('TopCities', True, False, city=self.city_name)
            cities = [[city.state, city.city] for city in city_objects]
        all_results = []
        try:
            for city in cities:
                self.current_city = city[1]
                self.current_state = city[0]
                result = {
                    'city': self.current_city,
                    'total': None,
                    'restaurants': []
                }
                self.logger.info('Starting to scrape {0}'.format(self.current_city))
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
        except HTTPError as error:
            self.logger.exception('Encountered HTTP error %s on %s:\nAbort program.', error.code, error.url)
        except:
            self.logger.exception('Something went wrong')
        finally:
            db.close_session()

    def _create_datastore_entity(self, content) -> dict:
        zip_code = content['address']['zip_code']
        attributes = {'updatedAt': datetime.datetime.now(),
                      'zip_code': zip_code,
                      'content': content,
                      'state': self.current_state,
                      'city': self.current_city,
                      'language': 'german',
                      'transported': False}
        return attributes
