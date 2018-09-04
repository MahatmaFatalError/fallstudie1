from config import constants
from main.helper import util
from main.helper.db_helper import DatastoreHelper, SqlHelper

datastore = DatastoreHelper()
sql = SqlHelper(constants.SQL_DATABASE_NAME)

util.setup_logging()

sql.create_session()

result = datastore.fetch_entity(constants.GCP_ENTITY_REVIEW,
                                None,
                                None,
                                True,
                                '=',
                                zip_code=68159,
                                transported=False)

sql.close_session()
