import logging
import re

from config import constants
from main.helper.db_helper import SqlHelper
from main.helper import util
from main.helper.yelp import YelpHelper

logger = logging.getLogger(__name__)


def main():
    restaurants = []
    util.setup_logging()

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    db.create_session()

    result = db.fetch_entity_where('Restaurant', True, city=None)

    yelp_helper = YelpHelper()

    for restaurant in result:
        restaurant_id = restaurant.id
        business, status_code = yelp_helper.get_business(restaurant_id)
        if 'location' in business:
            location = business['location']
            if 'zip_code' in location:
                zip_code = location['zip_code']
                if not zip_code:
                    zip_code = 0
                else:
                    integer_regex = re.compile('^[-+]?[0-9]+$')
                    match = integer_regex.match(zip_code)
                    if not match:
                        zip_code = 0
                restaurant.zip_code = zip_code
            else:
                logger.info('Zip Code not found')
            if 'address1' in location:
                street = location['address1']
                restaurant.street = street
            else:
                logger.info('Street not found')
            if 'city' in location:
                city = location['city']
                restaurant.city = city
            else:
                logger.info('City not found')
            if 'country' in location:
                country = location['country']
                restaurant.country = country
            else:
                logger.info('Country not found')
            if 'state' in location:
                state = location['state']
                restaurant.state = state
            else:
                logger.info('State not found')
            if 'price' in business:
                price_range = business['price']
                if price_range:
                    restaurant.price_range = price_range
                else:
                    logger.info('Price Range not found')
            restaurants.append(restaurant)

    for item in restaurants:
        db.insert(item)

    db.commit_session()
    db.close_session()


if __name__ == '__main__':
    main()