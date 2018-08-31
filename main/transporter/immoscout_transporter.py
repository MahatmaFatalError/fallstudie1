# coding=utf-8
import json
from main.transporter.transporter import Transporter


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
                entities.append(item)
        return entities