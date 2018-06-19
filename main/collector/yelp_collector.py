# -*- coding: utf-8 -*-
import datetime
import time

import requests
import logging
from main.helper.exception import YelpError
from google.api_core.exceptions import ServiceUnavailable
from config import constants
from main.collector.collector import Collector
from urllib.parse import quote
from main.database.db_helper import SqlHelper, DatastoreHelper
from urllib.error import HTTPError

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

    def collect(self):
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        db.create_session()
        cities = db.fetch_all(constants.SQL_TABLE_CITY)
        try:
            for city in cities:
                name = city.name
                for zip_code in city.zip_codes:
                    if not zip_code.requested:
                        zip_completed = True
                        self.location = str(zip_code.zip_code) + ', ' + str(name) + ', Deutschland'
                        logger.debug(self.location)
                        self.offset = 0
                        content = self._get_search(self.location, self.offset)
                        if 'error' not in content:
                            total = content['total']
                            save_success = self._save(content)
                            if save_success is False:
                                zip_completed = False
                            logger.info(u'Found {0} Entries...'.format(total))
                            while self.offset < total\
                                    and(self.offset + constants.YELP_SEARCH_LIMIT <= 1000)\
                                    and save_success is True:
                                content = self._get_search(self.location, self.offset)
                                self.offset += constants.YELP_SEARCH_LIMIT + 1
                                if 'error' not in content:
                                    save_success = self._save(content)
                                    if save_success is False:
                                        zip_completed = False
                                else:
                                    raise YelpError(content['error']['code'], content['error']['description'])
                        else:
                            raise YelpError(content['error']['code'], content['error']['description'])
                        if zip_completed is True:
                            zip_code.requested = True
                            db.commit_session()
        except HTTPError as error:
            logger.exception('Encountered HTTP error %s on %s:\nAbort program.', error.code, error.url)
        except YelpError as err:
            logger.exception(err)
        finally:
            db.close_session()

    def _get_search(self, location, offset):
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
        logger.info(u'Querying {0}; offset {1}...'.format(location, self.offset))
        return self._request(constants.YELP_SEARCH_PATH, url_params=url_params)

    def _save(self, data):
        result = False
        logger.info('Saving...')
        db = DatastoreHelper()
        attributes = {'path': self.current_path,
                      'location': self.location,
                      'offset': self.offset,
                      'updated_at': datetime.datetime.now(),
                      'content': data,
                      'transported': False}
        entity_id = str(self.current_path) + str(self.location) + str(self.offset)
        try:
            db.create_or_update(constants.GCP_ENTITY_RESTAURANT, entity_id, attributes)
            result = True
        except ServiceUnavailable:
            logger.exception('Service unavailable when trying to save %s', entity_id)
        except:
            logger.exception('An Unknown Error occured')
        return result

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
        logger.info(response.status_code)
        error_codes = [502, 503]
        while response.status_code in error_codes:
            time.sleep(0.1)
            logger.info(response.status_code)
            response = requests.request('GET', url, headers=self.headers, params=url_params)
            logger.info(response.status_code)
        return response.json()