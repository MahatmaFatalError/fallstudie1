#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from main.database.init_db import RestaurantCategory
from main.transporter.transporter import Transporter
import logging

logger = logging.getLogger(__name__)

zip_codes = None


class SpeisekarteTransporter(Transporter):

    def map(self, datastore_entity):
        entities = []

        return entities


