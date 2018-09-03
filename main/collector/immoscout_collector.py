# coding=utf-8
import datetime
import logging
from main.collector.collector import Collector
from config import constants
import requests
from requests_oauthlib import OAuth1
import pandas as pd
from main.helper.db_helper import DatastoreHelper, SqlHelper
from main.helper.result import Result

logger = logging.getLogger(__name__)


class ImmoscoutCollector(Collector):
    entity_id = None

    def __init__(self, entity_name, test_mode, entity_id):
        super(ImmoscoutCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode)
        self.entity_id = entity_id

    def _save(self, data):
        logger.info('Saving {} in Datastore...'.format(self.entity_name))
        success = False
        db = DatastoreHelper()
        attributes = {'updatedAt': datetime.datetime.now(), 'content': data, 'transported': False}
        key = db.create_or_update(self.entity_name, self.entity_id, attributes)
        if key:
            success = True
        return success

    def run(self):
        result = Result()
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        session = db.get_connection()
        df = pd.read_sql_table(table_name='top_city', con=session)
        top_n = 10
        cities = pd.DataFrame(data=df.iloc[0:top_n], columns={'city'})
        for index, row in cities.iterrows():
            print(str(index + 1) + ". " + row['city'])

        # cities = {
        #   'city': ['Berlin', 'Frankfurt am Main', 'München', 'Hamburg', 'Düsseldorf', 'Darmstadt', 'Köln', 'Hannover',
        #            'Bremen', 'Erfurt']}
        # cities = {'city': ['Heidelberg', 'Karlsruhe']}
        city_for_search = pd.DataFrame(cities, columns=['city'])

        immo_oauth = OAuth1(
            constants.IMMOSCOUT_CLIENT_KEY,
            client_secret=constants.IMMOSCOUT_CLIENT_SECRET,
            resource_owner_key=constants.IMMOSCOUT_RESOURCE_OWNER_KEY,
            resource_owner_secret=constants.IMMOSCOUT_RESOURCE_OWNER_SECRET)
        # create empty geo_df
        geo_df = pd.DataFrame(columns={'geoId', 'city'})

        # get geoid from Immoscout24 API
        for index, row in city_for_search.iterrows():
            immo_geo_url = constants.IMMOSCOUT_GEO_URL_1 + str(row['city']) + constants.IMMOSCOUT_GEO_URL_2
            immo_geo_response = requests.get(url=immo_geo_url,
                                             auth=immo_oauth,
                                             params=constants.IMMOSCOUT_HEADERS)
            immo_geo_response_json = pd.read_json(immo_geo_response.text)
            if not immo_geo_response_json.empty:
                geocode = pd.Series(immo_geo_response_json['entity'][0]['id'])
                geo_df = geo_df.append(pd.DataFrame({'geoId': geocode, 'city': row['city']}), ignore_index=True,
                                       sort=True)
                logger.info(
                    'Found Geocode from City: ' + str(row['city']) + ', Geocode: ' + str(geocode))
            else:
                logger.info("No Geocode for city: " + str(row['city']))
        logger.info(geo_df)

        # Fläche Retaurant:
        # https: // se909eeccf1caa559.jimcontent.com / download / version / 1507517357 / module / 11096440527 / name / AuszugDiplomarbeit_13.03.2006.pdf
        # Gast = 40 %
        # Technik = 12 %
        # Personal = 8 %
        # Gast = 40 %
        PLATZBEDARF_GAST = 1.5  # m²
        PLÄTZE_MIN = 52  # für 40.000 € = 100 %
        PLÄTZE_MAX = 65  # für 125 %
        TOTAL_FLÄCHE_MIN = PLATZBEDARF_GAST * PLÄTZE_MIN / 40 * 100.0
        TOTAL_FLÄCHE_MAX = PLATZBEDARF_GAST * PLÄTZE_MAX / 40 * 100.0

        restaurant_df = pd.DataFrame()
        # get Immoscout24 object by geocode
        for index, row in geo_df.iterrows():
            params = {'realestatetype': 'gastronomy',
                      'geocodes': str(row['geoId']),
                      'gastronomytypes': 'restaurant',
                      'channel': 'is24',
                      'numberofseats': str(PLÄTZE_MIN) + '-' + str(PLÄTZE_MAX),
                      'pagesize': '200',
                      'totalfloorspace': str(TOTAL_FLÄCHE_MIN) + '-' + str(TOTAL_FLÄCHE_MAX)
                      }
            immo_search_response = requests.request(method='GET',
                                                    url=constants.IMMOSCOUT_SEARCH_URL,
                                                    params=params,
                                                    headers=constants.IMMOSCOUT_HEADERS,
                                                    auth=immo_oauth)
            immo_search_json = pd.read_json(immo_search_response.text)
            hits = immo_search_json['resultlist.resultlist'][0]['numberOfHits']
            logger.info("Hits: " + str(hits) + " for city: " + str(row['city']) + "\r\n")
            if hits == 1:
                rest_dict = immo_search_json['resultlist.resultlist'][1][0]['resultlistEntry']['resultlist.realEstate']
                data = {'title': [rest_dict['title']],
                        'price': [rest_dict['price']['value']],
                        'marketingtype': [rest_dict['price']['marketingType']],
                        'currency': [rest_dict['price']['currency']],
                        'priceintervaltype': [rest_dict['price']['priceIntervalType']],
                        'postcode': [rest_dict['address']['postcode']],
                        'city': [rest_dict['address']['city']],
                        'quarter': [rest_dict['address']['quarter']],
                        'totalfloorspace': [rest_dict['totalFloorSpace']]}
                df = pd.DataFrame(data, columns={'title', 'price', 'marketingtype', 'currency', 'priceintervaltype',
                                                 'postcode', 'city', 'quarter', 'totalfloorspace'})
                restaurant_df = restaurant_df.append(df, ignore_index=True, sort=True)
            elif hits >= 1:
                for i in range(hits):
                    rest_dict = immo_search_json['resultlist.resultlist'][1][0]['resultlistEntry'][i][
                        'resultlist.realEstate']
                    data = {'title': [rest_dict['title']],
                            'price': [rest_dict['price']['value']],
                            'marketingtype': [rest_dict['price']['marketingType']],
                            'currency': [rest_dict['price']['currency']],
                            'priceintervaltype': [rest_dict['price']['priceIntervalType']],
                            'postcode': [rest_dict['address']['postcode']],
                            'city': [rest_dict['address']['city']],
                            'quarter': [rest_dict['address']['quarter']],
                            'totalfloorspace': [rest_dict['totalFloorSpace']]}
                    df = pd.DataFrame(data, columns={'title', 'price', 'marketingtype', 'currency', 'priceintervaltype',
                                                     'postcode', 'city', 'quarter', 'totalfloorspace'})
                    restaurant_df = restaurant_df.append(df, ignore_index=True, sort=True)
            else:
                logger.info('No object found for city: ' + str(row['city']))
        logger.info(restaurant_df)
        result_json = restaurant_df.to_json(orient='records')
        success = self._save(result_json)
        result.set_success(success)
        logger.info(result)
