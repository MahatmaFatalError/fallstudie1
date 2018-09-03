import logging
from statistics import mode, StatisticsError

from config import constants
from main.helper.db_helper import SqlHelper
from main.database.init_db import PriceRangeCalculated
from main.helper import util
from main.helper.exception import YelpError
from main.helper.yelp import YelpHelper

logger = logging.getLogger(__name__)


def check_price_range_availability_and_update():
    yelp_helper = YelpHelper()
    restaurants = []
    util.setup_logging()

    not_available_count = 0

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    db.create_session()

    result = db.fetch_entity_where('Restaurant', True, price_range=None)
    logger.info('Found {0} restaurants'.format(str(len(result))))

    try:
        for restaurant in result:
            restaurant_id = restaurant.id
            business, status_code = yelp_helper.get_business(restaurant_id)
            if 'error' not in business:
                if 'price' in business:
                    price_range = business['price']
                    if price_range:
                        restaurant.price_range = price_range
                    else:
                        logger.info('Price Range is null')
                    db.insert(restaurant)
                else:
                    not_available_count += 1
            else:
                raise YelpError(business['error']['code'], business['error']['description'])
            logger.info(not_available_count)
    except YelpError as error:
        logger.exception(error)
        logger.info('Adding {0} updated restaurants to DB...'.format(len(restaurants)))
    finally:
        db.commit_session()
        db.close_session()


def fill_price_range_calculated_table():
    util.setup_logging()
    city_mode_list = {}

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    db.create_session()

    restaurants_without_price = db.fetch_entity_where('Restaurant', True, price_range=None)
    logger.info('Found {0} restaurants without Price'.format(len(restaurants_without_price)))

    for restaurant_without_price in restaurants_without_price:
        price_range_calculated = PriceRangeCalculated()

        restaurant_id = restaurant_without_price.id
        price_range_calculated.restaurant_id = restaurant_id

        city_name = restaurant_without_price.city
        if city_name:
            if city_name not in city_mode_list:
                logger.info('Calculating mode for {0}'.format(city_name))
                price_range_list = []
                restaurants_of_city = db.fetch_entity_where('Restaurant', True, city=city_name)
                logger.info('Found {0} restaurants for {1}'.format(len(restaurants_of_city), city_name))
                for restaurant_of_city in restaurants_of_city:
                    price_range = restaurant_of_city.price_range
                    if price_range:
                        price_range_list.append(price_range)
                if len(price_range_list) > 0:
                    try:
                        price_range_mode = mode(price_range_list)
                        logger.info('Mode for {0}: {1}'.format(city_name, price_range_mode))
                    except StatisticsError:
                        price_range_mode = '-1'
                        logger.info('Multiple modes found for {0}'.format(city_name))
                else:
                    price_range_mode = '-2'
                    logger.info('No price_range attribute found in {0}'.format(city_name))
                city_mode_list[city_name] = price_range_mode
            else:
                price_range_mode = city_mode_list[city_name]
                logger.info('Found price_range {0} for {1}'.format(price_range_mode, city_name))
            price_range_calculated.price_range = price_range_mode
            db.insert(price_range_calculated)

    logger.info('Calculated {0} price_range mode(s)'.format(len(city_mode_list)))

    db.commit_session()
    db.close_session()


if __name__ == '__main__':
    # check_price_range_availability_and_update()
    fill_price_range_calculated_table()
