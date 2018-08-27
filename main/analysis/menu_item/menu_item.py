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

    result = defaultdict(defaultdict)

    datastore = DatastoreHelper()
    sql = SqlHelper(constants.SQL_DATABASE_NAME)

    sql.create_session()
    city_from_db = sql.fetch_city_by_name(city)
    sql.create_session()
    zip_codes = city_from_db.zip_codes
    for zip_code_object in zip_codes:
        zip_code = str(zip_code_object.zip_code)
        category_dict = defaultdict(defaultdict)
        # fav_items_all = defaultdict(int)

        # fetch restaurants from plz from datastore
        datastore_content = datastore.fetch_entity(
            constants.GCP_ENTITY_SPEISEKARTE,
            1000,
            0,
            '=',
            zip_code=zip_code
        )

        if datastore_content is not None:
            for entity in datastore_content:
                if 'content' in entity:
                    restaurant_string = json.dumps(entity['content'], ensure_ascii=False)
                    restaurant = json.loads(restaurant_string)

                    # create favorite items for restaurant
                    favs = restaurant['favourite_items']
                    fav_items = defaultdict(int)
                    if favs is not None:
                        for favoutite_item in favs:
                            item = favoutite_item.lower()
                            fav_items[item] += 1

                    # get category(ies) and build a category key
                    category_list = restaurant['categories']
                    if category_list is not None:
                        cat_string = '-'.join(category_list)
                    else:
                        cat_string = 'undefined'

                    # add favorite items to category
                    if cat_string in category_dict:
                        for key, value in category_dict[cat_string].items():
                            value += fav_items[key]
                    else:
                        category_dict[cat_string] = fav_items

        # create one key for one zip code
        result[zip_code] = category_dict

    result_string= json.dumps(result, ensure_ascii=False)
    result_json = json.loads(result_string)
    write_result(result_json, 'fav_items')


def write_result(result, title):
    with open('result/' + title + '.txt', 'w', encoding="utf-8") as outfile:
        json.dump(result, outfile, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    util.setup_logging()
    run()