from main.database.DBHelper import SqlHelper


db = SqlHelper('fonethd')
db.create_session()
entries = db.fetch_all('city')
for row in entries:
    print(row.zip_codes)