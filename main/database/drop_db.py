from config import constants
from main.database.DBHelper import SqlHelper
from main.database.init_db import City

db = SqlHelper(constants.SQL_DATABASE_NAME)
engine = db.get_connection()

City.__table__.drop(engine)