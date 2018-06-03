# -*- coding: utf-8 -*-
import datetime
import json

import requests
from config import constants
from main.collector.collector import Collector
from urllib.error import HTTPError
from urllib.parse import quote
from main.database.DBHelper import SqlHelper, DatastoreHelper
import logging


logger = logging.getLogger(__name__)


class YelpCollector(Collector):

    def __init__(self):
        Collector.__init__(self)
        self.host = constants.YELP_API_HOST
        self.headers = {
            'Authorization': 'Bearer %s' % constants.YELP_API_KEY,
        }
        self.location = None
        self.offset = None
        self.current_path = None

    def _save(self, data):
        db = DatastoreHelper()
        attributes = {'path': self.current_path,
                      'location': self.location,
                      'offset': self.offset,
                      'updated_at': datetime.datetime.now(),
                      'content': data}
        entity_id = str(self.current_path) + str(self.location) + str(self.offset)
        logger.debug(entity_id)
        db.create_or_update(constants.GCP_ENTITY_RESTAURANT, entity_id, attributes)

    def collect(self):
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        cities = db.select_all(constants.SQL_TABLE_CITY)
        for city in cities:
            self.location = str(city.zip_code) + ', DE'
            logger.debug(self.location)
            self.offset = 0
            result = self._get_search(self.location, self.offset)
            content = json.dumps(result)
            self._save(content)
            total = result['total']
            logger.info(u'Found {0} Entries...'.format(total))
            while self.offset < total and (self.offset + constants.YELP_SEARCH_LIMIT <= 1000):
                result = self._get_search(self.location, self.offset)
                self._save(result)
                self.offset += constants.YELP_SEARCH_LIMIT + 1

    def _get_search(self, location, offset):
        """Query the Search API by a search term and location.
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {
            'term': constants.YELP_SEARCH_TERM,
            'radius': constants.YELP_RADIUS,
            'limit': constants.YELP_SEARCH_LIMIT,
            'location': location.replace(' ', '+'),
            'offset': offset
        }
        logger.info(u'Querying {0}; offset {1}...'.format(location, self.offset))
        return self._request(constants.YELP_SEARCH_PATH, url_params=url_params)

    def _get_business(self, business_id):
        """Query the Business API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = constants.YELP_BUSINESS_PATH.replace('{id}', business_id)
        return self._request(constants.YELP_API_HOST, business_path)

    def _get_reviews(self, business_id):
        """Query the Review API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = constants.YELP_REVIEW_PATH.replace('{id}', business_id)

        return self._request(constants.YELP_API_HOST, business_path)

    def _request(self, path, url_params=None):
        """Given your API_KEY, send a GET request to the API.
        Args:
            path (str): The path of the API after the domain.
            url_params (dict): An optional set of query parameters in the request.
        Returns:
            dict: The JSON response from the request.
        Raises:
            HTTPError: An error occurs from the HTTP request.
        """
        url_params = url_params or {}
        url = '{0}{1}'.format(self.host, quote(path.encode('utf8')))
        self.current_path = url
        logger.info(u'Querying {0} ...'.format(url))

        response = requests.request('GET', url, headers=self.headers, params=url_params)
        return response.json()