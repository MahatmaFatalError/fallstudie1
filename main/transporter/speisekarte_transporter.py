#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from main.database.init_db import Speisekarte, FavouriteItem, RestaurantService, SpeisekarteCategory, MenuItem
from main.helper import util
from main.helper.yelp import YelpHelper
from main.transporter.transporter import Transporter
import logging

logger = logging.getLogger(__name__)


class SpeisekarteTransporter(Transporter):

    def map(self, datastore_entity):
        entities = []
        yelp = YelpHelper()
        ok_codes = [200, 201]
        if 'content' in datastore_entity:
            speisekarte = Speisekarte()
            content = datastore_entity['content']
            zip_code = datastore_entity['zip_code']
            speisekarte.zip_code = zip_code
            try:
                source_content = json.loads(content)
            except TypeError:
                source_content = content
            if 'id' in source_content:
                speisekarte_id = source_content['id']
                speisekarte.id = speisekarte_id

            if 'address' in source_content:
                street = source_content['address']['street']
                name = source_content['address']['name']
                speisekarte.city = self.city_name
                state_iso = util.map_city_to_state_iso_code(self.city_name)

                result_json, status_code = yelp.get_business_match(name, street, self.city_name, state_iso, zip_code)
                if status_code in ok_codes:
                    if 'businesses' in result_json:
                        business = result_json['businesses']
                        if len(business) > 0:
                            yelp_restaurant_id = business[0]['id']
                            speisekarte.yelp_restaurant_id = yelp_restaurant_id
                else:
                    speisekarte.yelp_restaurant_id = None

            # create favourite items
            if 'favourite_items' in source_content:
                fav_items_list = source_content['favourite_items']
                if fav_items_list is not  None and len(fav_items_list) > 0:
                    for item in fav_items_list:
                        fav_item = FavouriteItem()
                        # fav_item.speisekarte = speisekarte
                        fav_item.name = item
                        fav_item.datasource = 'speisekarte.de'
                        speisekarte.favourite_items.append(fav_item)

            # create services
            if 'services' in source_content:
                service_list = source_content['services']
                if service_list is not None and len(service_list) > 0:
                    for item in service_list:
                        service = RestaurantService()
                        # service.speisekarte = speisekarte
                        service.datasource = 'speisekarte.de'
                        service.name = item
                        speisekarte.restaurant_services.append(service)

            # create category with menu items
            if 'menu' in source_content:
                menu_list = source_content['menu']
                if menu_list is not None and len(menu_list) > 0:
                    for item in menu_list:
                        category = SpeisekarteCategory()
                        if 'category' in item:
                            category.name = item['category']
                            # category.speisekarte = speisekarte

                        if 'id'in item:
                            cat_id = item['id']
                            category.id = cat_id

                        # create menu items
                        if 'menu_items' in item:
                            menu_items = item['menu_items']
                            if menu_items is not None and len(menu_items) > 0:
                                for menu_item_string in menu_items:
                                    menu_item = MenuItem()
                                    # menu_item.category = category
                                    menu_item.name = menu_item_string
                                    menu_item.datasource = 'speisekarte.de'

                                    category.menu_items.append(menu_item)

                        speisekarte.categories.append(category)
            entities.append(speisekarte)
        return entities
