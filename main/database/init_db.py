from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from config import constants
from main.database.DBHelper import SqlHelper

Base = declarative_base()


class City(Base):
    __tablename__ = constants.SQL_CITY_TABLE

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    plz = Column(Integer)
    population = Column(Integer)

    def __repr__(self):
        return "<City(name='%s', plz='%d', population='%d')>" % (self.name, self.plz, self.population)


db = SqlHelper(constants.SQL_DATABASE_NAME)
engine = db.get_connection()
Base.metadata.create_all(engine)