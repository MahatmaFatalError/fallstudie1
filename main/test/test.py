from config import constants
from main.helper.db_helper import DatastoreHelper, SqlHelper

db = DatastoreHelper()
sql = SqlHelper(constants.SQL_DATABASE_NAME)

sql.create_session()

speisekarten = sql.fetch_entity_where('Speisekarte', True)

print(len(speisekarten))

# zip_codes_list = []
# sql.create_session()
#
# city_from_db = sql.fetch_city_by_name('Mannheim')
#
# # get zip codes and close session afterwards
# zip_codes = city_from_db.zip_codes
#
# sql.close_session()
#
# for zip in zip_codes:
#     zip_codes_list.append(zip.zip_code)
# total_all = []
# for item in zip_codes_list:
#     total = db.fetch_entity(entity_name=constants.GCP_ENTITY_SPEISEKARTE, operator='=', zip_code=str(item))
#     total_all += total
#
# print(len(total_all))