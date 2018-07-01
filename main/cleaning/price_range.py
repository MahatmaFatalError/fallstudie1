import logging

from config import constants
from main.database.db_helper import SqlHelper
from main.helper import util
from main.helper.yelp import YelpHelper

logger = logging.getLogger(__name__)


def main():
    yelp_helper = YelpHelper()
    restaurants = []
    util.setup_logging()

    not_available_count = 0

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    db.create_session()

    result = db.fetch_entity_where('Restaurant', True, price_range=None)
    logger.info('Found {0} restaurants'.format(str(len(result))))

    for restaurant in result:
        restaurant_id = restaurant.id
        business = yelp_helper.get_business(restaurant_id)
        if 'price' in business:
            price_range = business['price']
            if price_range:
                restaurant.price_range = price_range
            else:
                logger.info('Price Range is null')
            restaurants.append(restaurant)
        else:
            not_available_count += 1
        logger.info(not_available_count)

    for item in restaurants:
        db.insert(item)

    db.commit_session()
    db.close_session()


if __name__ == '__main__':
    main()