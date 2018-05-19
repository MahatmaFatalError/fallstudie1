# -*- coding: utf-8 -*-
import requests
from config import constants
from .collector import Collector
from urllib.parse import quote


class Yelp(Collector):

    def __init__(self):
        Collector.__init__(self)
        self.api_key = 'None'
        self.host = 'None'
        self.headers = {}

    def authenticate(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': 'Bearer %s' % api_key,
        }

    def set_host(self, host):
        self.host = host

    def collect(self, location, offset, term='restaurants'):
        """Query the Search API by a search term and location.
        Args:
            term (str): The search term passed to the API.
            offset (int): Offset the list of returned business results by this amount.
            location (str): The search location passed to the API.
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {
            'term': term.replace(' ', '+'),
            'radius': constants.YELP_RADIUS,
            'limit': constants.YELP_SEARCH_LIMIT,
            'location': location.replace(' ', '+'),
            'offset': offset
        }
        return self._request(constants.YELP_SEARCH_PATH, url_params=url_params)

    def get_business(self, business_id):
        """Query the Business API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = constants.YELP_BUSINESS_PATH.replace('{id}', business_id)

        return self._request(constants.YELP_API_HOST, business_path)

    def get_reviews(self, business_id):
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

        print(u'Querying {0} ...'.format(url))

        response = requests.request('GET', url, headers=self.headers, params=url_params)
        return response.json()