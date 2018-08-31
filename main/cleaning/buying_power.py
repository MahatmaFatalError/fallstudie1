import logging

from config import constants
from main.database.db_helper import SqlHelper
from main.database.init_db import BuyingPowerCalculated
from main.helper import util
from main.database.db_helper import DatastoreHelper
import json

logger = logging.getLogger(__name__)


def get_germany_buying_power_average():
    source_db = DatastoreHelper()
    buying_power_average = None

    source_entities = source_db.fetch_entity(constants.GCP_ENTITY_KAUFKRAFT, 1, 0, '=', transported=False)
    if source_entities:
        for datastore_entity in source_entities:
            if 'content' in datastore_entity:
                content = datastore_entity['content']
                try:
                    content = json.loads(content)
                except TypeError:
                    content = content
                for city in content:
                    name = city['city']
                    if name == 'Deutschland':
                        buying_power_average = city['buyingpower_2017_euro_a_head']
    return buying_power_average


def fill_buying_power_calculated_table():
    util.setup_logging()

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    db.create_session()

    cities_without_buying_power = db.fetch_entity_where('City', True, buying_power=None)
    logger.info('Found {0} cities without Buying Power'.format(len(cities_without_buying_power)))

    buying_power_average = get_germany_buying_power_average()
    logger.info('Buying Power Germany: {0}'.format(buying_power_average))

    for city_without_buying_power in cities_without_buying_power:
        buying_power_calculated = BuyingPowerCalculated()

        city_id = city_without_buying_power.id
        buying_power_calculated.city_id = city_id
        buying_power_calculated.buying_power = buying_power_average

        db.insert(buying_power_calculated)

    db.commit_session()
    db.close_session()


if __name__ == '__main__':
    fill_buying_power_calculated_table()
