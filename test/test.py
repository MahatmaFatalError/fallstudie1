
# only for testing purposes
from config import constants
from main.database.db_helper import DatastoreHelper

source_db = DatastoreHelper()

total = source_db.get_total(constants.GCP_ENTITY_RESTAURANT, only_not_yet_transported=True)
print(total)


