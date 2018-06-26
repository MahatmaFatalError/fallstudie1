import csv

from config import constants
from main.database.db_helper import SqlHelper

data = []

with open('del2.csv') as csv_data:
    csv_reader = csv.DictReader(csv_data, delimiter=',', quotechar='"')
    column_names = csv_reader.fieldnames
    for row in csv_reader:
        item = {}
        for name in column_names:
            attribute = row[name]
            item[name] = attribute
        if item[name] != '':
            data.append(item)

if data:
    db = SqlHelper(database=constants.SQL_DATABASE_NAME)
    db.create_session()
    for item in data:
        long = float(item['Column 2'].replace(',', '.'))
        lat = float(item['Column 1'].replace(',', '.'))
        if long and lat:
            result = db.find_restaurant_by_long_lat(long=long, lat=lat)
            for itm in result:
                print(itm)
    db.commit_session()
    db.close_session()