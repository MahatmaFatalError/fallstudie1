import logging
import time
import requests
from urllib.parse import quote
from config import constants

logger = logging.getLogger(__name__)


class YelpHelper:

    def get_search(self, location, offset):
        """Query the Search API by a search term and location.
        Returns:
            dict: The JSON response from the request.
        """

        url_params = {
            'term': constants.YELP_SEARCH_TERM,
            'limit': constants.YELP_SEARCH_LIMIT,
            'location': location.replace(' ', '+'),
            'offset': offset
        }
        logger.info(u'Querying {0}; offset {1}...'.format(location, offset))
        return self._request(constants.YELP_SEARCH_PATH, url_params=url_params)

    def get_business(self, business_id):
        """Query the Business API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = constants.YELP_BUSINESS_PATH.replace('{id}', business_id)
        return self._request(business_path)

    def get_reviews(self, business_id):
        """Query the Review API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        review_path = constants.YELP_REVIEW_PATH.replace('{id}', business_id)

        return self._request(review_path)

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
        url = '{0}{1}'.format(constants.YELP_API_HOST, quote(path.encode('utf8')))
        self.current_path = url
        logger.info(u'Querying {0} ...'.format(url))
        headers = {'Authorization': 'Bearer %s' % constants.YELP_API_KEY}
        response = requests.request('GET', url, headers=headers, params=url_params)
        logger.info('HTTP Code: {0}'.format(response.status_code))
        error_codes = [502, 503]
        while response.status_code in error_codes:
            time.sleep(0.1)
            logger.info('HTTP Code: {0}'.format(response.status_code))
            response = requests.request('GET', url, headers=headers, params=url_params)
            logger.info('HTTP Code: {0}'.format(response.status_code))
        return response.json()