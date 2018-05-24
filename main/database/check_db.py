from main.database.DBHelper import SqlHelper


db = SqlHelper('fonethd')
entries = db.select_all('city')
for row in entries:
    print(row)