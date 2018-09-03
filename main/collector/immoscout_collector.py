# coding=utf-8
import datetime
from main.collector.collector import Collector
from config import constants
import requests
from requests_oauthlib import OAuth1
import pandas as pd
from main.helper.db_helper import SqlHelper
from main.helper.result import Result


class ImmoscoutCollector(Collector):

    entity_id = None

    def __init__(self, entity_name, test_mode, entity_id):
        super(ImmoscoutCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode)
        self.entity_id = entity_id

    def _create_datastore_entity(self, data) -> dict:
        attributes = {'updatedAt': datetime.datetime.now(), 'content': data, 'transported': False}
        return attributes

    def run(self):
        result = Result()
        db = SqlHelper(constants.SQL_DATABASE_NAME)
        session = db.get_connection()
        df = pd.read_sql_table(table_name='top_city', con=session)
        top_n = 10
        cities = pd.DataFrame(data=df.iloc[0:top_n], columns={'city'})
        for index, row in cities.iterrows():
            self.logger.debug(str(index + 1) + ". " + row['city'])

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
                self.logger.info(
                    'Found Geocode from City: ' + str(row['city']) + ', Geocode: ' + str(geocode))
            else:
                self.logger.info("No Geocode for city: " + str(row['city']))
        self.logger.info(geo_df)

        # Fläche Retaurant:
        # https: // se909eeccf1caa559.jimcontent.com / download / version / 1507517357 / module / 11096440527 / name / AuszugDiplomarbeit_13.03.2006.pdf
        # Gast = 40 %
        # Technik = 12 %
        # Personal = 8 %
        # Gast = 40 %
        platzbedarf_gast = 1.5  # m²
        plaetze_min = 52  # für 40.000 € = 100 %
        plaetze_max = 65  # für 125 %
        total_flaeche_min = platzbedarf_gast * plaetze_min / 40 * 100.0
        total_flaeche_max = platzbedarf_gast * plaetze_max / 40 * 100.0

        restaurant_df = pd.DataFrame()
        # get Immoscout24 object by geocode
        for index, row in geo_df.iterrows():
            params = {'realestatetype': 'gastronomy',
                      'geocodes': str(row['geoId']),
                      'gastronomytypes': 'restaurant',
                      'channel': 'is24',
                      'numberofseats': str(plaetze_min) + '-' + str(plaetze_max),
                      'pagesize': '200',
                      'totalfloorspace': str(total_flaeche_min) + '-' + str(total_flaeche_max)
                      }
            immo_search_response = requests.request(method='GET',
                                                    url=constants.IMMOSCOUT_SEARCH_URL,
                                                    params=params,
                                                    headers=constants.IMMOSCOUT_HEADERS,
                                                    auth=immo_oauth)
            immo_search_json = pd.read_json(immo_search_response.text)
            hits = immo_search_json['resultlist.resultlist'][0]['numberOfHits']
            self.logger.info("Hits: " + str(hits) + " for city: " + str(row['city']) + "\r\n")
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
                self.logger.info('No object found for city: ' + str(row['city']))
        self.logger.info(restaurant_df)
        result_json = restaurant_df.to_json(orient='records')
        attributes = self._create_datastore_entity(result_json)
        success = self._save(self.entity_id, attributes)
        result.set_success(success)
        self.logger.info(result)
        return result
