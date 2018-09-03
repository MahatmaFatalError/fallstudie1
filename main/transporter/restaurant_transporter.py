#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json

from config import constants
from main.database.init_db import Restaurant, FoodCategory, RestaurantTransaction
from main.transporter.transporter import Transporter


class RestaurantTransporter(Transporter):

    def map(self, datastore_entity):
        datastore_zip_code = datastore_entity['location'].split(',')[0]
        self.logger.debug(datastore_zip_code)
        entities = []
        if 'content' in datastore_entity:
            content = datastore_entity['content']
            try:
                source_content = json.loads(content)
            except TypeError:
                source_content = content
            now = datetime.datetime.now()
            if 'businesses' in source_content:
                businesses = source_content['businesses']
                for business in businesses:
                    if 'location' in business:
                        restautant_zip_code = business['location']['zip_code']
                        if restautant_zip_code:
                            # only map restaurants with the searched zip code
                            if datastore_zip_code == restautant_zip_code:
                                restaurant = Restaurant()
                                restaurant.id = business['id']
                                restaurant.updated_at = now
                                if 'name' in business:
                                    restaurant.name = business['name']
                                restaurant.datasource = constants.DATASOURCE_YELP
                                if 'is_closed' in business:
                                    restaurant.is_closed = business['is_closed']
                                if 'price' in business:
                                    restaurant.price_range = business['price']
                                if 'coordinates' in business:
                                    restaurant.latitude = business['coordinates']['latitude']
                                    restaurant.longitude = business['coordinates']['longitude']
                                if 'rating' in business:
                                    restaurant.rating = business['rating']
                                if 'review_count' in business:
                                    review_count = business['review_count']
                                    if not review_count:
                                        restaurant.review_count = 0
                                if 'categories' in business:
                                    categories = business['categories']
                                    for category_entity in categories:
                                        category = FoodCategory()
                                        category.name = category_entity['title']
                                        category.alias = category_entity['alias']
                                        category.updated_at = now
                                        category.restaurant_id = restaurant.id
                                        restaurant.food_categories.append(category)
                                if 'transactions' in business:
                                    transactions = business['transactions']
                                    for transaction_string in transactions:
                                        transaction = RestaurantTransaction()
                                        transaction.restaurant_id = restaurant.id
                                        transaction.updated_at = now
                                        transaction.name = transaction_string
                                        restaurant.transactions.append(transaction)
                                if 'location' in business:
                                    location = business['location']
                                    if 'zip_code' in location:
                                        zip_code = location['zip_code']
                                        if not zip_code:
                                            zip_code = 0
                                        restaurant.zip_code = zip_code
                                    if 'address1' in location:
                                        street = location['address1']
                                        restaurant.street = street
                                    if 'city' in location:
                                        city = location['city']
                                        restaurant.city = city
                                        self.logger.debug('City of Restaurant: {0}'.format(city))
                                    if 'country' in location:
                                        country = location['country']
                                        restaurant.country = country
                                    if 'state' in location:
                                        state = location['state']
                                        restaurant.state = state
                                entities.append(restaurant)
                            else:
                                self.logger.info("zip doesn't match --> skip")
                        else:
                            self.logger.info("no zip code --> skip")
                    else:
                        self.logger.info("no location --> skip")
        return entities
