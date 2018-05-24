from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric
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

    def __repr__(self):
        return "<City(name='%s', zip_code='%s', population='%s')>" % (self.name, self.zip_code, self.population)


db = SqlHelper(constants.SQL_DATABASE_NAME)
engine = db.get_connection()
Base.metadata.create_all(engine)