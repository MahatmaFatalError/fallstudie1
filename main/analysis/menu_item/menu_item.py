import json
import logging
from collections import defaultdict

from config import constants
from main.database.db_helper import DatastoreHelper, SqlHelper
from main.helper import util

logger = logging.getLogger(__name__)
city = 'Mannheim'


def run():
    global city
    datastore = DatastoreHelper()
    sql = SqlHelper(constants.SQL_DATABASE_NAME)

    fav_items = defaultdict(int)
    categories = defaultdict(int)
    menu_items = defaultdict(int)
    services = defaultdict(int)

    sql.create_session()
    city_from_db = sql.fetch_city_by_name(city)
    sql.create_session()
    zip_codes = city_from_db.zip_codes
    for zip_code in zip_codes:
        datastore_content = datastore.fetch_entity(
            constants.GCP_ENTITY_SPEISEKARTE,
            1000,
            0,
            '=',
            zip_code=zip_code.zip_code
        )
        if datastore_content is not None:
            for entity in datastore_content:
                if 'content' in entity:
                    restaurant_string = json.dumps(entity['content'], ensure_ascii=False)
                    restaurant = json.loads(restaurant_string)
                    favs = restaurant['favourite_items']
                    if favs is not None:
                        for favoutite_item in favs:
                            item = favoutite_item.lower()
                            fav_items[item] += 1
                    cats = restaurant['categories']
                    if cats is not None:
                        for category in cats:
                            categories[category] += 1
                    menu = restaurant['menu']
                    if menu is not None:
                        for item in menu:
                            items = item['menu_items']
                            for x in items:
                                menu_items[x] += 1
                    servs = restaurant['services']
                    if servs is not None:
                        for service in servs:
                            services[service] += 1

    result_string= json.dumps(fav_items, ensure_ascii=False)
    result = json.loads(result_string)
    # write_result(result, 'fav_items')


def write_result(result, title):
    with open('result/' + title + '.txt', 'w') as outfile:
        json.dump(result, outfile, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    util.setup_logging()
    run()