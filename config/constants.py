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
YELP_BUSINESS_PATH = '/v3/businesses/{id}'  # Business ID will come after slash.
YELP_REVIEW_PATH = 'v3/businesses/{id}/reviews'
YELP_API_KEY = 'f27wx-PAgrGJvZQ2lbTbRQDXMVGDgkcUt8hX2AhgDe1sIxODCmxHmb3hoKZL0Qt0b5KvlAO9HCctWR6Qcz16dF1VUhk_8rEgerP5VO3UtPOjrLGt8ucp2AQtOeruWnYx'
YELP_RADIUS = 40000
YELP_SEARCH_LIMIT = 50
YELP_SEARCH_TERM = 'restaurants'

# GCP constants
GCP_ENTITY_LOCATION = 'THD_City'
GCP_ENTITY_RESTAURANT = 'THD_Restaurant'
GCP_ENTITY_PLZ_CITY= 'THD_Plz_for_City'
GCP_ENTITY_KAUFKRAFT = 'THD_Kaufkraft'
GCP_ENTITY_RENT = 'THD_Rent'
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
SQL_TABLE_BUYING_POWER = 'buying_power'
SQL_TABLE_RENT = 'buying_power'
SQL_TABLE_PRICE_RANGE='price_range_calculated'