from main.factory import EverythingFactory
from config import constants


class Creator:

    @staticmethod
    def create_city_collector(test_mode, city_name, top_how_much):
        city_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                  constants.CSV,
                                                  'german_cities',
                                                  constants.GCP_ENTITY_LOCATION,
                                                  test_mode,
                                                  'data/staedte.csv',
                                                  constants.CSV_DELIMITER_SEMI)
        return city_collector

    @staticmethod
    def create_plz_collector(test_mode, city_name, top_how_much):
        plz_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                 constants.CSV,
                                                 'german_plz_for_cities',
                                                 constants.GCP_ENTITY_PLZ_CITY,
                                                 test_mode,
                                                 'data/plz_ort.csv',
                                                 constants.CSV_DELIMITER_COMMA,
                                                 'utf-8')
        return plz_collector

    @staticmethod
    def create_restaurant_collector(test_mode, city_name, top_how_much):
        yelp_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                  'restaurant',
                                                  constants.GCP_ENTITY_RESTAURANT,
                                                  test_mode,
                                                  city_name,
                                                  top_how_much)
        return yelp_collector

    @staticmethod
    def create_speisekarte_collector(test_mode, city_name, top_how_much):
        speisekarte_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                         'speisekarte',
                                                         constants.GCP_ENTITY_SPEISEKARTE,
                                                         test_mode,
                                                         city_name,
                                                         top_how_much)
        return speisekarte_collector

    @staticmethod
    def create_kaufkraft_collector(test_mode, city_name, top_how_much):
        kaufkraft_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                       'kaufkraft',
                                                       'kaufkraft_for_germany',
                                                       constants.GCP_ENTITY_KAUFKRAFT,
                                                       test_mode,
                                                       'data/kaufkraft.pdf')
        return kaufkraft_collector

    @staticmethod
    def create_rent_collector(test_mode, city_name, top_how_much):
        rent_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                  'rent',
                                                  constants.GCP_ENTITY_RENT,
                                                  test_mode,
                                                  'data/rent.json')
        return rent_collector

    @staticmethod
    def create_immoscout_collector(test_mode, city_name, top_how_much):
        immoscout_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                       'immoscout',
                                                       constants.GCP_ENTITY_IMMOSCOUT,
                                                       test_mode,
                                                       'immoscout_top_cities',
                                                       city_name,
                                                       top_how_much)
        return immoscout_collector

    @staticmethod
    def create_review_collector(test_mode, city_name, top_how_much):
        review_collector = EverythingFactory.create(constants.FACTORY_COLLECTOR,
                                                    'review',
                                                    constants.GCP_ENTITY_REVIEW,
                                                    test_mode,
                                                    city_name,
                                                    top_how_much)
        return review_collector

    @staticmethod
    def create_plz_transporter(test_mode, city_name, top_how_much):
        plz_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                   'plz',
                                                   constants.SQL_DATABASE_NAME,
                                                   constants.GCP_ENTITY_PLZ_CITY,
                                                   test_mode,
                                                   city_name,
                                                   top_how_much)
        return plz_transporter

    @staticmethod
    def create_city_transporter(test_mode, city_name, top_how_much):
        csv_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                   'city',
                                                   constants.SQL_DATABASE_NAME,
                                                   constants.GCP_ENTITY_LOCATION,
                                                   test_mode,
                                                   city_name,
                                                   top_how_much)
        return csv_transporter

    @staticmethod
    def create_restaurant_transporter(test_mode, city_name, top_how_much):
        restaurant_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                          'restaurant',
                                                          constants.SQL_DATABASE_NAME,
                                                          constants.GCP_ENTITY_RESTAURANT,
                                                          test_mode,
                                                          city_name,
                                                          top_how_much)
        return restaurant_transporter

    @staticmethod
    def create_kaufkraft_transporter(test_mode, city_name, top_how_much):
        kaufkraft_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                         'kaufkraft',
                                                         constants.SQL_DATABASE_NAME,
                                                         constants.GCP_ENTITY_KAUFKRAFT,
                                                         test_mode,
                                                         city_name,
                                                         top_how_much)
        return kaufkraft_transporter

    @staticmethod
    def create_rent_transporter(test_mode, city_name, top_how_much):
        kaufkraft_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                         'rent',
                                                         constants.SQL_DATABASE_NAME,
                                                         constants.GCP_ENTITY_RENT,
                                                         test_mode,
                                                         city_name,
                                                         top_how_much)
        return kaufkraft_transporter

    @staticmethod
    def create_speisekarte_transporter(test_mode, city_name, top_how_much):
        speisekarte_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                           'speisekarte',
                                                           constants.SQL_DATABASE_NAME,
                                                           constants.GCP_ENTITY_SPEISEKARTE,
                                                           test_mode,
                                                           city_name,
                                                           top_how_much)
        return speisekarte_transporter

    @staticmethod
    def create_immoscout_transporter(test_mode, city_name, top_how_much):
        immoscout_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                         'immoscout',
                                                         constants.SQL_DATABASE_NAME,
                                                         constants.GCP_ENTITY_IMMOSCOUT,
                                                         test_mode,
                                                         city_name,
                                                         top_how_much)
        return immoscout_transporter

    @staticmethod
    def create_review_transporter(test_mode, city_name, top_how_much):
        immoscout_transporter = EverythingFactory.create(constants.FACTORY_TRANSPORTER,
                                                         'review',
                                                         constants.SQL_DATABASE_NAME,
                                                         constants.GCP_ENTITY_REVIEW,
                                                         test_mode,
                                                         city_name,
                                                         top_how_much)
        return immoscout_transporter
