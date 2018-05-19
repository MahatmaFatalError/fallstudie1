from DBHelper import DBHelper
import collector
import config
# TODO: Logging https://www.loggly.com/ultimate-guide/python-logging-basics/


def read_csv():
    db = DBHelper()
    csv_collector = collector.create('csv')

    csv_collector.collect('data/staedte.csv')
    content = csv_collector.get_data()
    # save entities in database
    for item in content:
        attributes = {'name': item['Stadt'], 'population': item['Bevölkerung gesamt'], 'plz': item['Postleitzahl']}
        city_id = item['Lfd. Nr.']
        # split additional "Stadt" Prefix from name cell
        name = attributes['name']
        name = name.split(',')[0]
        attributes['name'] = name
        if name:
            print(u'Creating {0} ...'.format(name))
           # db.create_or_update('City', city_id, attributes)


def save_businesses():
    db = DBHelper()
    yelp_collector = collector.create('yelp')
    yelp_collector.authenticate(config.YELP_API_KEY)
    yelp_collector.set_host(config.YELP_API_HOST)
    cities = db.list_all_entities('City')
    for city in cities:
        location = city['plz'] + ', DE'
        city_id = city.key
        print(u'Querying {0} ...'.format(location))
        offset = 0
        result = yelp_collector.collect(location, offset)
        total = result['total']
        print(u'Found {0} Entries...'.format(total))
        # db.create_or_update('Restaurant', city_id, {'total_restaurants': total})
        while offset < total:
            result = yelp_collector.collect(location, offset)
            key = 'businesses'
            if key in result:
                businesses = result[key]
                for business in businesses:
                    business_id = business['id']
                    attributes = {
                        'alias': business['alias'],
                        'name': business['name'],
                        'lat': business['coordinates']['latitude'],
                        'long': business['coordinates']['longitude']
                    }
                    db.create_or_update('Restaurant', business_id, attributes)
                offset += config.YELP_SEARCH_LIMIT + 1
            else:
                print(u'Key "{0} not found in query result ...'.format(key))


if __name__ == '__main__':
    read_csv()
    # save_businesses()