# -*- coding: utf-8 -*-

import requests
import config

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


class YelpHelper:

    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
        self.headers = {
            'Authorization': 'Bearer %s' % api_key,
        }

    def search(self, term, location):
        """Query the Search API by a search term and location.
        Args:
            term (str): The search term passed to the API.
            location (str): The search location passed to the API.
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {
            'term': term.replace(' ', '+'),
            'radius': config.YELP_RADIUS,
            'limit': config.YELP_SEARCH_LIMIT,
            'location': location.replace(' ', '+')
        }
        return self.request(config.YELP_SEARCH_PATH, url_params=url_params)

    def get_business(self, business_id):
        """Query the Business API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = config.YELP_BUSINESS_PATH.replace('{id}', business_id)

        return self._request(config.YELP_API_HOST, business_path)

    def get_reviews(self, business_id):
        """Query the Review API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = config.YELP_REVIEW_PATH.replace('{id}', business_id)

        return self._request(config.YELP_API_HOST, business_path)

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