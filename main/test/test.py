from config import constants
from main.database.db_helper import DatastoreHelper

db = DatastoreHelper()
result = db.fetch_entity(constants.GCP_ENTITY_SPEISEKARTE, 1, 0, '=', zip_code='44534')
print(result)