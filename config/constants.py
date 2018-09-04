# Python Constants
FACTORY_COLLECTOR = 'collector'
FACTORY_TRANSPORTER = 'transporter'
CSV = 'csv'
CSV_DELIMITER_COMMA = ','
CSV_DELIMITER_SEMI = ';'
DATASOURCE_YELP = 'yelp'

# Yelp API constants
YELP_API_HOST = 'https://api.yelp.com'
YELP_SEARCH_PATH = '/v3/businesses/search'
YELP_MATCH_PATH = '/v3/businesses/matches'
YELP_BUSINESS_PATH = '/v3/businesses/{id}'  # Business ID will come after slash.
YELP_REVIEW_PATH = '/v3/businesses/{id}/reviews'
YELP_API_KEY = 'f27wx-PAgrGJvZQ2lbTbRQDXMVGDgkcUt8hX2AhgDe1sIxODCmxHmb3hoKZL0Qt0b5KvlAO9HCctWR6Qcz16dF1VUhk_8rEgerP5VO3UtPOjrLGt8ucp2AQtOeruWnYx'
YELP_RADIUS = 40000
YELP_SEARCH_LIMIT = 50
YELP_SEARCH_TERM = 'restaurants'

# Immoscout24 API constants
IMMOSCOUT_GEO_URL_1 = 'https://rest.immobilienscout24.de/restapi/api/gis/v2.0/geoautocomplete/DEU?i='
IMMOSCOUT_GEO_URL_2 = '&t=city'
IMMOSCOUT_SEARCH_URL = 'https://rest.immobilienscout24.de/restapi/api/search/v1.0/search/region'
IMMOSCOUT_HEADERS = {'content-type': 'application/json',
                     'Accept': 'application/json'}
IMMOSCOUT_CLIENT_KEY = 'RestaurantLocationKey'
IMMOSCOUT_CLIENT_SECRET = 'CBFSz9Td16yBwVpj'
IMMOSCOUT_RESOURCE_OWNER_KEY = 'efeb00da-852d-417a-97c2-ed8d16214ca4'
IMMOSCOUT_RESOURCE_OWNER_SECRET = '8vqhdDfgnV0nJuY4wyCj24DEiM/rR6XnrThqdW9gqsXl3GIZEYPcvy6KU+LUKNTxazbsRKCaZBdo6gG7wUb/Bi6AU/t5i3lzm8+i1LywC4U='

# GCP constants
GCP_ENTITY_LOCATION = 'THD_City'
GCP_ENTITY_RESTAURANT = 'THD_Restaurant'
GCP_ENTITY_PLZ_CITY = 'THD_Plz_for_City'
GCP_ENTITY_KAUFKRAFT = 'THD_Kaufkraft'
GCP_ENTITY_RENT = 'THD_Rent'
GCP_ENTITY_SPEISEKARTE = 'THD_Speisekarte'
GCP_ENTITY_IMMOSCOUT = 'THD_Immoscout'
GCP_ENTITY_REVIEW = 'THD_Review'
GCP_FETCH_LIMIT = 500

# SQL Constants
SQL_DATABASE_NAME = 'fonethd'
SQL_DATABASE_USER = 'postgres'
SQL_DATABASE_PW = 'team123'
SQL_DATABASE_PORT = '5432'
SQL_DATABASE_HOST = '35.190.205.207'

SQL_TABLE_CITY = 'city'
SQL_TABLE_RESTAURANT = 'restaurant'
SQL_TABLE_FOOD_CATEGORY = 'food_category'
SQL_TABLE_RESTAURANT_TRANSACTION = 'restaurant_transaction'
SQL_TABLE_REVIEW = 'review'
SQL_TABLE_ZIP_CODE = 'zip_code'
SQL_TABLE_BUYING_POWER = 'buying_power_calculated'
SQL_TABLE_SERVICE = 'restaurant_service'
SQL_TABLE_PRICE_RANGE = 'price_range_calculated'
SQL_TABLE_RENT_AVG = 'rent_avg_calculated'
SQL_TABLE_CATEGORY = 'speisekarte_category'
SQL_TABLE_MENU_ITEM = 'menu_item'
SQL_TABLE_FAV_ITEM = 'favourite_item'
SQL_TABLE_MENU = 'speisekarte'
SQL_TABLE_SEAT = 'restaurant_seat'
SQL_TABLE_IMMOSCOUT = 'immoscout'
SQL_TABLE_TOP_CITY = 'top_city'
SQL_TABLE_RATING_WORD = 'top_rating_word'
