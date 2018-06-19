#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from config import constants
from main.database.init_db import Restaurant, FoodCategory, RestaurantTransaction
from main.transporter.transporter import Transporter
import logging

logger = logging.getLogger(__name__)


class RestaurantTransporter(Transporter):

    def map(self, source_content):
        # TODO: map empty integers to 0
        logger.info('Starting Mapping for %s entries', source_content)
        entities = []
        key = 'businesses'
        now = datetime.datetime.now()
        if key in source_content:
            businesses = source_content[key]
            for business in businesses:
                logger.debug(business)
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
                restaurant.latitude = business['coordinates']['latitude']
                restaurant.longitude = business['coordinates']['longitude']
                if 'rating' in business:
                    restaurant.rating = business['rating']
                if 'review_count' in business:
                    restaurant.review_count = business['review_count']
                if 'categories' in business:
                    categories = business['categories']
                    for category_entity in categories:
                        logger.debug(category_entity)
                        category = FoodCategory()
                        category.name = category_entity['title']
                        category.alias = category_entity['alias']
                        category.updated_at = now
                        category.restaurant_id = restaurant.id
                        restaurant.food_categories.append(category)
                if 'transactions' in business:
                    transactions = business['transactions']
                    for transaction_string in transactions:
                        logger.debug(transaction_string)
                        transaction = RestaurantTransaction()
                        transaction.restaurant_id = restaurant.id
                        transaction.updated_at = now
                        transaction.name = transaction_string
                        restaurant.transactions.append(transaction)
                if 'location' in business:
                    location = business['location']
                    zip_code = location['zip_code']
                    street = location['address1']
                    city = location['city']
                    country = location['country']
                    state = location['state']
                    restaurant.city = city
                    restaurant.country = country
                    restaurant.state = state
                    restaurant.zip_code = zip_code
                    restaurant.street = street
                logging.debug(restaurant)
                entities.append(restaurant)
        return entities
