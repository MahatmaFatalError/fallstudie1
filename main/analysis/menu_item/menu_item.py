import json
import logging
import pandas as pd
from collections import defaultdict
from config import constants
from main.database.db_helper import DatastoreHelper, SqlHelper
from main.helper import util

logger = logging.getLogger(__name__)


def run():
    # city_string = str(input("Type in the city you want to analyze!. Name is case-sensitive!"))
    # For testing purposes
    city_string = 'Mannheim'

    # action = int(input("Which action do you want to perform? (1) Group or (2) Count?"))
    # For testing purposes
    action = 2

    # fetch city from db
    zip_codes = fetch_zip_codes_from_database(city_string)

    if action is 2:  # count action
        fav_items, categories, services, menu_items = create_count_city(zip_codes)
        write_result(fav_items, 'fav_items_count')
        write_result(categories, 'categories_count')
        write_result(services, 'services_count')
        write_result(menu_items, 'menu_items_count')
    elif action is 1:  # group action
        result = create_favourite_items(zip_codes)
        write_result(result, 'fav_items_group')


def fetch_zip_codes_from_database(city_string):
    sql = SqlHelper(constants.SQL_DATABASE_NAME)
    sql.create_session()
    city_from_db = sql.fetch_city_by_name(city_string)
    while city_from_db is None:
        city_string = str(input("City {0} not available in database. Try again!".format(city_string)))
        city_from_db = sql.fetch_city_by_name(city_string)

    # get zip codes and close session afterwards
    zip_codes = city_from_db.zip_codes
    sql.close_session()

    return zip_codes


def create_count_city(zip_codes):

    fav_items = defaultdict(int)
    categories = defaultdict(int)
    menu_items = defaultdict(int)
    services = defaultdict(int)

    for zip_code_object in zip_codes:
        zip_code = str(zip_code_object.zip_code)
        datastore_content = fetch_restaurant_by_zip_code(zip_code)
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

    # sort dictionaries by count
    fav_items = sorted(fav_items.items(), key=lambda elem: elem[1], reverse=True)
    categories = sorted(categories.items(), key=lambda elem: elem[1], reverse=True)
    menu_items = sorted(menu_items.items(), key=lambda elem: elem[1], reverse=True)
    services = sorted(services.items(), key=lambda elem: elem[1], reverse=True)

    return fav_items, categories, services, menu_items


def fetch_restaurant_by_zip_code(zip_code):
    datastore = DatastoreHelper()

    datastore_content = datastore.fetch_entity(
        constants.GCP_ENTITY_SPEISEKARTE,
        1000,
        0,
        '=',
        zip_code=zip_code
    )
    return datastore_content


def create_favourite_items(zip_codes):
    result = defaultdict(defaultdict)

    for zip_code_object in zip_codes:
        zip_code = str(zip_code_object.zip_code)

        # fetch restaurants from plz from datastore
        datastore_content = fetch_restaurant_by_zip_code(zip_code)

        if datastore_content is not None:
            # create one key for one zip code
            result[zip_code] = create_favoutite_items_plz(datastore_content)

    return result


def create_favoutite_items_plz(datastore_content):
    category_dict = defaultdict(defaultdict)

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
    return category_dict


def write_result(result, title):
    with open('result/' + title + '.txt', 'w', encoding="utf-8") as outfile:
        json.dump(result, outfile, indent=4, ensure_ascii=False)


def analyze_result(result):
    # convert result to dataframe
    # json_data = json.dumps(result)
    fav_items = pd.DataFrame.from_dict(result)
    kaefertal = fav_items[fav_items['68309'].notnull()]['68309']
    kaefertal_list = kaefertal.tolist()
    # italienisch = fav_items.loc['italienisch', '68309']
    # print(italienisch)
    # visualize it


if __name__ == '__main__':
    util.setup_logging()
    run()