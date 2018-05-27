'''
Created on 25.05.2018

@author: hannes
'''
import requests
import urllib, json
from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from builtins import str

# GCP connection
db = create_engine('postgres://postgres:team123@35.190.205.207:5432/fonethd')
base = declarative_base()

class City(base):
    __tablename__ = 'worldcities'
    id = Column(Integer, primary_key=True)
    country = Column(String)
    fullcityname = Column(String)
    population = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)

Session = sessionmaker(bind=db)
session = Session()
base.metadata.create_all(db)
choose_city = input("Choose a City: ")

try:
    for latitude, longitude, population, country, fullcityname in session.query(City.latitude, City.longitude, City.population, City.country, City.fullcityname).filter_by(fullcityname=choose_city).filter_by(country='de').filter(City.population != None).limit(1):
        foo = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(latitude) + "," + str(longitude) + "&radius=" + str(population) + "&type=foot&key=AIzaSyDoTq1BpqS_LrUvJpARbVdgcUwc-Iv5_ks"
except Exception as e:
    print( "<p>Error: %s</p>" % str(e) )

bar = str(foo)
#print(bar)
response = requests.get(bar)
response.json()
jsonObj = response.json()
#jsonObj["results"]
#print(response.text)
# write in a file
with open('GP_output.json', 'w') as outfile:
    json.dump(jsonObj["results"], outfile)
