from DBHelper import DBHelper
from CSVReader import CSVReader
from YelpHelper import YelpHelper
import config


def read_csv():
    db = DBHelper()
    reader = CSVReader()

    reader.read('data/staedte.csv')
    content = reader.get_data()
    # save entities in database
    for item in content:
        attributes = {'name': item['Stadt'], 'population': item['Bevölkerung gesamt']}
        city_id = item['Lfd. Nr.']
        # split additional "Stadt" Prefix from name cell
        name = attributes['name']
        name = name.split(',')[0]
        attributes['name'] = name
        if name:
            print(u'Creating {0} ...'.format(name))
            db.create_or_update('City', city_id, attributes)


def save_businesses():
    db = DBHelper()
    yelp = YelpHelper(config.YELP_API_HOST, config.YELP_API_KEY)
    cities = db.list_all_entities('City')
    for city in cities:
        location = city['name']
        city_id = city.key
        print(city_id)
        print(u'Querying {0} ...'.format(location))
        offset = 0
        result = yelp.search(location, offset)
        total = result['total']
        # db.create_or_update('Restaurant', 1, {'total_restaurants': total})
        while offset < total:
            result = yelp.search(location, offset)
            businesses = result['businesses']
            for business in businesses:
                business_id = business['id']
                attributes = {
                    'alias': business['alias'],
                    'name': business['name'],
                    'lat': business['coordinates']['latitude'],
                    'long': business['coordinates']['longitude']
                }
                print(attributes)
                # db.create_or_update('Restaurant', business_id, attributes)
            offset += config.YELP_SEARCH_LIMIT + 1


if __name__ == '__main__':
    # read_csv()
    save_businesses()