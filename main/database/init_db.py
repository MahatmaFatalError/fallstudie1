from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Boolean
from config import constants
from main.database.DBHelper import SqlHelper


Base = declarative_base()


class City(Base):
    __tablename__ = constants.SQL_CITY_TABLE

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    zip_code = Column(Integer)
    population = Column(Integer)
    size_sqkm = Column(Numeric)
    population_sqkm = Column(Numeric)
    total_restaurants = Column(Integer, nullable=True)


class Restaurant(Base):
    __tablename__ = constants.SQL_RESTAURANT_TABLE

    id = Column(Integer, primary_key=True, autoincrement=False)
    datasource = Column(String)
    name = Column(String)
    price_range = Column(String(5))
    rating = Column(Numeric)
    is_closed = Column(Boolean)
    review_count = Column(Integer)
    longitude = Column(Numeric, nullable=False)
    latitude = Column(Numeric, nullable=False)


class FoodCategory(Base):
    __tablename__ = constants.SQL_RESTAURANT_TABLE

    business_id = Column(Integer, primary_key=True, autoincrement=False)
    alias = Column(String)
    name = Column(String)


db = SqlHelper(constants.SQL_DATABASE_NAME)
engine = db.get_connection()
Base.metadata.create_all(engine)