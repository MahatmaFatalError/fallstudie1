from main.factory import EverythingFactory
from config import constants


class Creator:

    @staticmethod
    def create_city_collector():
        city_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                  constants.CSV,
                                                  'german_cities',
                                                  constants.GCP_ENTITY_LOCATION,
                                                  'data/staedte.csv',
                                                  constants.CSV_DELIMITER_SEMI)
        return city_collector

    @staticmethod
    def create_plz_collector():
        plz_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                 constants.CSV,
                                                 'german_plz_for_cities',
                                                 constants.GCP_ENTITY_PLZ_CITY,
                                                 'data/plz_ort.csv',
                                                 constants.CSV_DELIMITER_COMMA,
                                                 'utf-8',
                                                 True)
        return plz_collector

    @staticmethod
    def create_restaurant_collector():
        yelp_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                  'yelp',
                                                  constants.GCP_ENTITY_RESTAURANT,
                                                  False)
        return yelp_collector

    @staticmethod
    def create_kaufkraft_collector():
        kaufkraft_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                       'kaufkraft',
                                                       'kaufkraft_for_germany',
                                                       constants.GCP_ENTITY_KAUFKRAFT,
                                                       'data/kaufkraft.pdf'
                                                       )
        return kaufkraft_collector

    @staticmethod
    def create_rent_collector():
        rent_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                  'rent',
                                                  constants.GCP_ENTITY_RENT,
                                                  False,
                                                  'data/rent.json'
                                                  )
        return rent_collector

    @staticmethod
    def create_plz_transporter(test_mode):
        plz_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                   'plz',
                                                   constants.SQL_DATABASE_NAME,
                                                   constants.GCP_ENTITY_PLZ_CITY,
                                                   constants.SQL_TABLE_CITY,
                                                   True,
                                                   test_mode)
        return plz_transporter

    @staticmethod
    def create_city_transporter(test_mode):
        csv_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                   'city',
                                                   constants.SQL_DATABASE_NAME,
                                                   constants.GCP_ENTITY_LOCATION,
                                                   constants.SQL_TABLE_CITY,
                                                   False,
                                                   test_mode)
        return csv_transporter

    @staticmethod
    def create_restaurant_transporter(test_mode):
        restaurant_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                          'restaurant',
                                                          constants.SQL_DATABASE_NAME,
                                                          constants.GCP_ENTITY_RESTAURANT,
                                                          constants.SQL_TABLE_RESTAURANT,
                                                          False,
                                                          test_mode)
        return restaurant_transporter

    @staticmethod
    def create_kaufkraft_transporter(test_mode):
        kaufkraft_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                         'kaufkraft',
                                                         constants.SQL_DATABASE_NAME,
                                                         constants.GCP_ENTITY_KAUFKRAFT,
                                                         constants.SQL_TABLE_BUYING_POWER,
                                                         False,
                                                         test_mode)
        return kaufkraft_transporter
