# -*- coding: utf-8 -*-
import datetime
import logging
from google.api_core.exceptions import ServiceUnavailable
from config import constants
from main.collector.collector import Collector
from main.database.db_helper import SqlHelper, DatastoreHelper
from urllib.error import HTTPError
from main.helper.jessy_spider import SpeisekarteSpider

logger = logging.getLogger(__name__)


class SpeisekarteCollector(Collector):

    def __init__(self, entity_name):
        super(SpeisekarteCollector, self).__init__(
            entity_name=entity_name
        )
        self.city = None

    def run(self):
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        db.create_session()
        cities = db.fetch_all(constants.SQL_TABLE_CITY)
        all_results = []
        try:
            for city in cities:
                self.city = city.name
                result = {
                    'city': self.city,
                    'total': None,
                    'restaurants': []
                }
                spider = SpeisekarteSpider(self.city)
                spider.run()
                spider_result = spider.get_result()
                success = spider_result.get_success()
                if success:
                    data = spider_result.get_data()
                    restaurants = data['restaurants']
                    total = data['total']
                    result['total'] = total
                    for restaurant in restaurants:
                        success = self._save(restaurant)
                        restaurant_result = {
                            'success': success,
                            'content': restaurant['id']
                        }
                        result['restaurants'].append(restaurant_result)
                all_results.append(result)
            logger.info(all_results)
        except HTTPError as error:
            logger.exception('Encountered HTTP error %s on %s:\nAbort program.', error.code, error.url)
        except:
            logger.exception('Something went wrong')
        finally:
            db.close_session()

    def _save(self, restaurant):
        logger.info('Saving {} in Datastore...'.format(self.entity_name))
        result = False
        db = DatastoreHelper()
        zip_code = restaurant['address']['zip_code']
        attributes = {"updatedAt": datetime.datetime.now(), "zip_code": zip_code, "content": restaurant, "transported": False}
        restaurant_id = restaurant['id']
        entity_id = self.city + '$' + restaurant_id
        try:
            db.create_or_update(self.entity_name, entity_id, attributes)
            result = True
        except ServiceUnavailable:
            logger.exception('Service unavailable when trying to save %s', entity_id)
        except:
            logger.exception('An Unknown Error occured')
        return result
