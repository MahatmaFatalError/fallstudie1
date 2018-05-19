from helper.DBHelper import DBHelper
import collector
from config import constants
import os
import json
import logging.config
import logging

logger = logging.getLogger(__name__)

def setup_logging(default_path='config/logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration"""

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def read_csv():
    db = DBHelper()
    csv_collector = collector.create('csv')

    csv_collector.collect('data/staedte.csv')
    content = csv_collector.get_data()
    # save entities in database
    for item in content:
        attributes = {'name': item['Stadt'], 'population': item['Bevölkerung gesamt'], 'plz': item['Postleitzahl']}
        city_id = item['Lfd. Nr.']
        # split additional "Stadt" Prefix from name cell
        name = attributes['name']
        name = name.split(',')[0]
        attributes['name'] = name
        if name:
            logger.info('Creating %s ...',name)
            db.create_or_update(constants.GCP_LOCATION_ENTITY, city_id, attributes)


def save_businesses():
    db = DBHelper()
    yelp_collector = collector.create('yelp')
    yelp_collector.authenticate(constants.YELP_API_KEY)
    yelp_collector.set_host(constants.YELP_API_HOST)
    cities = db.list_all_entities('City')
    for city in cities:
        location = city['plz'] + ', DE'
        city_id = city.key
        print(u'Querying {0} ...'.format(location))
        offset = 0
        result = yelp_collector.collect(location, offset)
        total = result['total']
        print(u'Found {0} Entries...'.format(total))
        # db.create_or_update('Restaurant', city_id, {'total_restaurants': total})
        while offset < total:
            result = yelp_collector.collect(location, offset)
            key = 'businesses'
            if key in result:
                businesses = result[key]
                for business in businesses:
                    business_id = business['id']
                    attributes = {
                        'alias': business['alias'],
                        'name': business['name'],
                        'lat': business['coordinates']['latitude'],
                        'long': business['coordinates']['longitude']
                    }
                    db.create_or_update(constants.GCP_RESTAURANT_ENTITY, business_id, attributes)
                offset += constants.YELP_SEARCH_LIMIT + 1
            else:
                print(u'Key "{0} not found in query result ...'.format(key))


if __name__ == '__main__':
    setup_logging()
    read_csv()
    # save_businesses()