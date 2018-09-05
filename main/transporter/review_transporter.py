#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from main.database.init_db import Review
from main.transporter.transporter import Transporter


class ReviewTransporter(Transporter):

    def map(self, datastore_entity):
        entities = []
        review = Review()
        restaurant_id = None
        language = None
        try:
            source_content = json.loads(datastore_entity)
        except TypeError:
            source_content = datastore_entity
        if 'restaurant_id' in source_content:
            restaurant_id = source_content['restaurant_id']
        if 'locale' in source_content:
            locale = source_content['locale']
            if locale == 'en_US':
                language = 'english'
            elif locale == 'de_DE':
                language = 'german'
        if 'content' in source_content:
            content = source_content['content']
            total = content['total']
            if total > 1:
                reviews = content['reviews']
                for review_json in reviews:
                    rating = review_json['rating']
                    time_created = review_json['time_created']
                    text = review_json['text']
                    review_id = review_json['id']

                    review.restaurant_id = restaurant_id
                    review.id = review_id
                    review.datasource = 'yelp'
                    review.text = text
                    review.created_at = time_created
                    review.rating = rating
                    review.language = language

                    entities.append(review)

        return entities
