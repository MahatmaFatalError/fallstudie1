from config import constants
from main.database.db_helper import SqlHelper
from main.database.init_db import City, Restaurant, RestaurantTransaction, FoodCategory, ZipCode

db = SqlHelper(constants.SQL_DATABASE_NAME)
engine = db.get_connection()

RestaurantTransaction.__table__.drop(engine)
FoodCategory.__table__.drop(engine)
Restaurant.__table__.drop(engine)
