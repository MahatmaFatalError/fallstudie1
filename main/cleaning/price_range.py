import logging

from config import constants
from main.database.db_helper import SqlHelper
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
            business = yelp_helper.get_business(restaurant_id)
            if 'error' not in business:
                if 'price' in business:
                    price_range = business['price']
                    if price_range:
                        restaurant.price_range = price_range
                    else:
                        logger.info('Price Range is null')
                    restaurants.append(restaurant)
                else:
                    not_available_count += 1
            else:
                raise YelpError(business['error']['code'], business['error']['description'])
            logger.info(not_available_count)
    except YelpError as error:
        logger.exception(error)
        logger.info('Adding {0} updated restaurants to DB...'.format(len(restaurants)))
        for item in restaurants:
            db.insert(item)
        db.commit_session()
    finally:
        db.close_session()


def fill_price_range_with_modus_of_city():
    yelp_helper = YelpHelper()
    restaurants = []
    util.setup_logging()

    not_available_count = 0

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    db.create_session()

    result = db.fetch_entity_where('Restaurant', True, price_range=None)
    logger.info('Found {0} restaurants'.format(len(result)))

    for restaurant in restaurants:
        city = restaurant.city


if __name__ == '__main__':
    check_price_range_availability_and_update()
    # fill_price_range_with_modus_of_city()
