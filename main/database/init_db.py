from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config import constants
# from main.database.DBHelper import SqlHelper

Base = declarative_base()


class City(Base):
    __tablename__ = constants.SQL_TABLE_CITY

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    population = Column(Integer)
    size_sqkm = Column(Numeric)
    population_sqkm = Column(Numeric)
    zip_codes = relationship('ZipCode')


class ZipCode(Base):
    __tablename__ = constants.SQL_TABLE_ZIP_CODE

    city_id = Column(Integer, ForeignKey(constants.SQL_TABLE_CITY + '.id'), primary_key=True, autoincrement=False)
    zip_code = Column(Integer, primary_key=True)


class Restaurant(Base):
    __tablename__ = constants.SQL_TABLE_RESTAURANT

    id = Column(Integer, primary_key=True, autoincrement=False)
    datasource = Column(String)
    name = Column(String)
    price_range = Column(String(5))
    rating = Column(Numeric)
    is_closed = Column(Boolean)
    review_count = Column(Integer)
    longitude = Column(Numeric, nullable=False)
    latitude = Column(Numeric, nullable=False)
    food_categories = relationship('FoodCategory')
    transactions = relationship('RestaurantTransaction')


class FoodCategory(Base):
    __tablename__ = constants.SQL_TABLE_FOOD_CATEGORY

    restaurant_id = Column(Integer, ForeignKey(constants.SQL_TABLE_RESTAURANT + '.id'), primary_key=True, autoincrement=False)
    alias = Column(String, primary_key=True)
    name = Column(String, primary_key=True)


class RestaurantTransaction(Base):
    __tablename__ = constants.SQL_TABLE_RESTAURANT_TRANSACTION

    restaurant_id = Column(Integer, ForeignKey(constants.SQL_TABLE_RESTAURANT + '.id'), primary_key=True, autoincrement=False)
    name = Column(String, primary_key=True)


# db = SqlHelper(constants.SQL_DATABASE_NAME)
# engine = db.get_connection()
# Base.metadata.create_all(engine)