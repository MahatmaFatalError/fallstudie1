import json
import logging
import pandas as pd
from collections import defaultdict
from config import constants
from helper.text_analyzer import TextAnalyzer
from main.helper.db_helper import DatastoreHelper, SqlHelper
from main.helper import util
import re

logger = logging.getLogger(__name__)
city_string = 'Bochum'
save_as_latex = True
action = 2  # 1 = group, 2 = just count

tree_tagger_dir = '../../../data/tree_tagger'
analyzer = TextAnalyzer('german', True, True, tree_tagger_dir)


def run():
    global action

    # fetch city from db
    zip_codes = fetch_zip_codes_from_database()

    if action is 2:  # count action
        fav_items, categories, services, menu_items = create_count_city(zip_codes)
        write_result(fav_items, 'fav_items_count')
        write_result(categories, 'categories_count')
        write_result(services, 'services_count')
        write_result(menu_items, 'menu_items_count')
    elif action is 1:  # group action
        result = create_favourite_items(zip_codes)
        write_result(result, 'fav_items_group')


def fetch_zip_codes_from_database():
    global city_string
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
                            item = process_item(favoutite_item)
                            if item:
                                fav_items[item] += 1
                    cats = restaurant['categories']
                    if cats is not None:
                        for category in cats:
                            category = process_item(category)
                            if category:
                                categories[category] += 1
                    menu = restaurant['menu']
                    if menu is not None:
                        for item in menu:
                            items = item['menu_items']
                            for x in items:
                                x = process_item(x)
                                if x:
                                    menu_items[x] += 1
                    servs = restaurant['services']
                    if servs is not None:
                        for service in servs:
                            service = process_item(service)
                            if service:
                                services[service] += 1

    # sort dictionaries by count
    fav_items = sorted(fav_items.items(), key=lambda elem: elem[1], reverse=True)
    categories = sorted(categories.items(), key=lambda elem: elem[1], reverse=True)
    menu_items = sorted(menu_items.items(), key=lambda elem: elem[1], reverse=True)
    services = sorted(services.items(), key=lambda elem: elem[1], reverse=True)

    return fav_items, categories, services, menu_items


def process_item(item):
    items = analyzer.text_process(item)
    item = ' '.join(items)
    # item = re.sub(r'\W+', ' ', item)
    return item


def fetch_restaurant_by_zip_code(zip_code):
    datastore = DatastoreHelper()

    datastore_content = datastore.fetch_entity(
        entity_name=constants.GCP_ENTITY_SPEISEKARTE,
        limit=1000,
        offset=0,
        operator='=',
        only_keys=False,
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
    global city_string
    global save_as_latex

    title += ('_' + city_string.lower())

    if not save_as_latex:
        with open('result/' + title + '.txt', 'w', encoding="utf-8") as outfile:
            json.dump(result, outfile, indent=4, ensure_ascii=False)
    else:
        if action == 2:
            item_column = []
            count_column = []
            for item in result:
                item_column.append(item[0])
                count_column.append(item[1])
            result_dict = {
                'item': item_column,
                'count': count_column
            }
            df = pd.DataFrame.from_dict(result_dict)
            # write df to tex file
            with open('result/' + title + '.tex', 'w', encoding='utf-8') as result_tex:
                result_tex.write(df.to_latex())


if __name__ == '__main__':
    util.setup_logging()
    run()