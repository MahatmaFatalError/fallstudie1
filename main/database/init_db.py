from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config import constants

Base = declarative_base()

# City Classes #


class ZipCode(Base):
    __tablename__ = constants.SQL_TABLE_ZIP_CODE

    city_id = Column(Integer, ForeignKey(constants.SQL_TABLE_CITY + '.id'), primary_key=True, autoincrement=False)
    zip_code = Column(Integer, primary_key=True)
    requested = Column(Boolean, default=False)
    updated_at = Column(DateTime)
    review_collected = Column(Boolean, default=False)

    def __str__(self):
        return 'city id: {0}, zip code: {1}, requested: {2}, updated_at: {3}, review_collected: {4}' \
            .format(self.city_id, self.zip_code, self.requested, self.updated_at, self.review_collected)


class City(Base):
    __tablename__ = constants.SQL_TABLE_CITY

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    population = Column(Integer)
    size_sqkm = Column(Numeric)
    population_sqkm = Column(Numeric)
    zip_codes = relationship('ZipCode')
    updated_at = Column(DateTime)
    buying_power = Column(Numeric)
    rent_avg = Column(Numeric)

    def __str__(self):
        return 'id: {0}, name: {1}, updated at: {2} buying power: {3}' \
            .format(self.id, self.name, self.updated_at, self.buying_power)


# Speisekarte Classes #

class Speisekarte(Base):
    __tablename__ = constants.SQL_TABLE_MENU

    id = Column(String, primary_key=True, autoincrement=False)
    yelp_restaurant_id = Column(String)
    zip_code = Column(Integer)
    city = Column(String)
    favourite_items = relationship('FavouriteItem')
    restaurant_services = relationship('RestaurantService')
    categories = relationship('SpeisekarteCategory')


class SpeisekarteCategory(Base):
    __tablename__ = constants.SQL_TABLE_CATEGORY

    id = Column(Integer, primary_key=True, autoincrement=False)
    speisekarte = Column(String, ForeignKey(constants.SQL_TABLE_MENU + '.id'))
    name = Column(String)
    menu_items = relationship('MenuItem')


class RestaurantService(Base):
    __tablename__ = constants.SQL_TABLE_SERVICE

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    datasource = Column(String)
    speisekarte = Column(String, ForeignKey(constants.SQL_TABLE_MENU + '.id'))


class MenuItem(Base):
    __tablename__ = constants.SQL_TABLE_MENU_ITEM

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Integer, ForeignKey(constants.SQL_TABLE_CATEGORY + '.id'))
    name = Column(String)
    datasource = Column(String)


class FavouriteItem(Base):
    __tablename__ = constants.SQL_TABLE_FAV_ITEM

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    datasource = Column(String)
    speisekarte = Column(String, ForeignKey(constants.SQL_TABLE_MENU + '.id'))


# Yelp Classes #


class Review(Base):
    __tablename__ = constants.SQL_TABLE_REVIEW

    id = Column(String, primary_key=True, autoincrement=False)
    datasource = Column(String)
    created_at = Column(DateTime)
    text = Column(String)
    restaurant_id = Column(String, ForeignKey(constants.SQL_TABLE_RESTAURANT + '.id'))
    rating = Column(Numeric)
    language = Column(String)


class Restaurant(Base):
    __tablename__ = constants.SQL_TABLE_RESTAURANT

    id = Column(String, primary_key=True, autoincrement=False)
    datasource = Column(String)
    name = Column(String)
    price_range = Column(String(5))
    rating = Column(Numeric)
    is_closed = Column(Boolean)
    review_count = Column(Integer)
    longitude = Column(Numeric)
    latitude = Column(Numeric)
    food_categories = relationship('FoodCategory', cascade="all, delete-orphan")
    transactions = relationship('RestaurantTransaction', cascade="all, delete-orphan")
    street = Column(String)
    zip_code = Column(Integer)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    updated_at = Column(DateTime)


class FoodCategory(Base):
    __tablename__ = constants.SQL_TABLE_FOOD_CATEGORY

    restaurant_id = Column(String, ForeignKey(constants.SQL_TABLE_RESTAURANT + '.id'), primary_key=True,
                           autoincrement=False)
    alias = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    updated_at = Column(DateTime)


class RestaurantTransaction(Base):
    __tablename__ = constants.SQL_TABLE_RESTAURANT_TRANSACTION

    restaurant_id = Column(String, ForeignKey(constants.SQL_TABLE_RESTAURANT + '.id'), primary_key=True,
                           autoincrement=False)
    name = Column(String, primary_key=True)
    updated_at = Column(DateTime)


class PriceRangeCalculated(Base):
    __tablename__ = constants.SQL_TABLE_PRICE_RANGE

    restaurant_id = Column(String, ForeignKey(constants.SQL_TABLE_RESTAURANT + '.id'), primary_key=True,
                           autoincrement=False)
    price_range = Column(String(5), primary_key=True)


class BuyingPowerCalculated(Base):
    __tablename__ = constants.SQL_TABLE_BUYING_POWER

    city_id = Column(Integer, ForeignKey(constants.SQL_TABLE_CITY + '.id'), primary_key=True,
                     autoincrement=False)
    buying_power = Column(Numeric, primary_key=True)


class RentAvgCalculated(Base):
    __tablename__ = constants.SQL_TABLE_RENT_AVG

    city_id = Column(Integer, ForeignKey(constants.SQL_TABLE_CITY + '.id'), primary_key=True,
                     autoincrement=False)
    rent_avg = Column(Numeric, primary_key=True)


class Immoscout(Base):
    __tablename__ = constants.SQL_TABLE_IMMOSCOUT

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String)
    city = Column(String)
    quarter = Column(String)
    postcode = Column(Integer)
    price = Column(Integer)
    currency = Column(String)
    marketingtype = Column(String)
    priceintervaltype = Column(String)
    totalfloorspace = Column(Numeric)

    def __str__(self):
        return 'id: {0}, name: {1}, updated at: {2} immoscout: {3}' \
            .format(self.id, self.name, self.updated_at, self.city)


class TopCities(Base):
    __tablename__ = constants.SQL_TABLE_TOP_CITY

    city = Column(String, primary_key=True, autoincrement=False)
    state = Column(String)
    potential = Column(Numeric)


if __name__ == '__main__':
    from main.helper.db_helper import SqlHelper

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    engine = db.get_connection()
    Base.metadata.create_all(engine)
