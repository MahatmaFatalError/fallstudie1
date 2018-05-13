from DBHelper import DBHelper
from CSVReader import CSVReader
from YelpHelper import YelpHelper
import config


db = DBHelper()
reader = CSVReader()
yelp = YelpHelper(config.YELP_API_HOST, config.YELP_API_KEY)

reader.read('data/staedte.csv')
content = reader.get_data()
# save entities in database
for item in content:
    name = item['Stadt']
    population = item['Bevölkerung gesamt']
    # split additional "Stadt" Prefix from name cell
    name = name.split(',')[0]
    if name is not None:
        print(u'Creating {0} ...'.format(name))
        db.create_city(name, population)

cities = db.list_all_entities('City')
for city in cities:
    location = city['name']
    print(u'Querying {0} ...'.format(location))
    offset = 0
    result = yelp.search(location, offset)
    total = result['total']
    while offset < total:
        result = yelp.search(location, offset)
        businesses = result['businesses']
        for business in businesses:
            alias = business['alias']
            name = business['name']
            lat = business['coordinates']['latitude']
            long = business['coordinates']['longitude']
            db.create_restaurant(alias, name, lat, long)
        offset += config.YELP_SEARCH_LIMIT