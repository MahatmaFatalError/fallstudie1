# coding=utf-8
import json
import logging
from main.transporter.transporter import Transporter
from main.database.init_db import Immoscout

logger = logging.getLogger(__name__)


class ImmoscoutTransporter(Transporter):

    def map(self, datastore_entity):
        entities = []
        if 'content' in datastore_entity:
            content = datastore_entity['content']
            try:
                source_content = json.loads(content)
            except TypeError:
                source_content = content
            for item in source_content:
                target_entity = Immoscout()
                target_entity.city = item['city']
                target_entity.currency = item['currency']
                target_entity.title = item['title']
                target_entity.marketingtype = item['marketingtype']
                target_entity.postcode = item['postcode']
                target_entity.price = item['price']
                target_entity.priceintervaltype = item['priceintervaltype']
                target_entity.quarter = item['quarter']
                target_entity.totalfloorspace = item['totalfloorspace']
                entities.append(target_entity)
        return entities
