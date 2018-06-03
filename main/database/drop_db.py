from config import constants
from main.database.DBHelper import SqlHelper
from main.database.init_db import City, Restaurant, RestaurantTransaction, FoodCategory, ZipCode

db = SqlHelper(constants.SQL_DATABASE_NAME)
engine = db.get_connection()

ZipCode.__table__.drop(engine)
City.__table__.drop(engine)
RestaurantTransaction.__table__.drop(engine)
FoodCategory.__table__.drop(engine)
Restaurant.__table__.drop(engine)