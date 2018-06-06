from main.database.db_helper import SqlHelper


db = SqlHelper('fonethd')
db.create_session()
entries = db.fetch_all('city')
for row in entries:
    zip_codes = row.zip_codes
    name = row.name
    print('Zip Codes for' + str(name))
    for zip_code in zip_codes:
        print(zip_code.zip_code)