import logging
from config import constants
from main.helper.db_helper import SqlHelper
from main.helper import util
from main.helper.yelp import YelpHelper

logger = logging.getLogger(__name__)


def main():
    util.setup_logging()

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    yelp = YelpHelper()
    db.create_session()

    result = db.fetch_entity_where('Restaurant', True, False, review_count=0)
    logger.info('Found {0} Restaurants with 0 Review Count'.format(len(result)))

    for restaurant in result:
        logger.info('Old Review Count Value: {0}'.format(restaurant.review_count))
        name = restaurant.name
        business_id = restaurant.id
        logger.info(name)
        result, status_code = yelp.get_business(business_id, 0)
        status_codes = [403, 404]
        if status_code not in status_codes:
            if 'error' not in result:
                review_count = result['review_count']
                if review_count is not None:
                    restaurant.review_count = review_count
                    logger.info('New Review Count Value: {0}'.format(restaurant.review_count))
            else:
                logger.error('{0}: {1}'.format(result['error']['code'], result['error']['description']))
                break
        else:
            restaurant.review_count = 0
            logger.info('New Review Count Value: {0}'.format(restaurant.review_count))

    db.commit_session()
    db.close_session()


if __name__ == '__main__':
    main()