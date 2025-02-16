from config import constants
from main.helper import util
from main.helper.db_helper import DatastoreHelper, SqlHelper
import pandas as pd

from main.helper.text_analyzer import TextAnalyzer

datastore = DatastoreHelper()
sql = SqlHelper(constants.SQL_DATABASE_NAME)

sql.create_session()

# df = sql.fetch_table_as_dataframe('top_cities')
# cities = pd.DataFrame(data=df.iloc[0:10], columns={'city', 'state'})
# cities = cities.values.tolist()

# city_objects = sql.fetch_entity_where('TopCities')
# cities = [[city.state, city.city] for city in city_objects]
# print(cities[1])
# print(cities[0])

analyzer = TextAnalyzer('english', True, False, '../../data/tree_tagger')

review = 'Yes, the 5 stars are deserved: here you can drink and buy the best coffee in Bochum (and maybe in the Ruhr area?). I usually only take the roasted coffee'

text = analyzer.text_process(review)

print(text)
#
# menu_item_improved = util.convert_list_to_string(analyzer.text_process(text))
# if menu_item_improved:
#     print('Item: ')
#     print(menu_item_improved)
# else:
#     print('Value is None')

# result = datastore.fetch_entity('THD_Speisekarte', None, None, True, '=', transported=False, zip_code=44866)
# print(result)

# sql._update_entity('ZipCode', 'zip_code', '10115', 'review_collected', False)

sql.commit_session()

sql.close_session()
