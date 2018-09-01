# coding=utf-8

from config import constants
import pandas as pd

# get access to DB

BUDGET = 750000 # €
BUY_FACTOR = 1 # einmal kaufen
RENT_FACTOR = 12 # für ein Jahr Miete
EINRICHTUNGS_KOSTEN_PER_SQUARE_METER = 1500 #TODO: bezieht sich auf welche Fläche? totalfloor or guest area?
EINRICHTUNG_PER_SEAT = 200
PLÄTZE_MIN = 52  # für 40.000 € = 100 %
PLÄTZE_MAX = 65  # für 125 %


def calc(price, priceintervaltype, totalfloorspace, seats):
    if 'ONE_TIME_CHARGE' in str(priceintervaltype):
        multiplier = BUY_FACTOR
    else:
        multiplier = RENT_FACTOR
    print('multipier: ' + str(multiplier))
    rest_budget = BUDGET - price * multiplier - EINRICHTUNGS_KOSTEN_PER_SQUARE_METER * totalfloorspace - seats * EINRICHTUNG_PER_SEAT
    return rest_budget


if __name__ == '__main__':
    from main.database.db_helper import SqlHelper

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    session = db.get_connection()
    immo_df = pd.read_sql_table(table_name='immoscout', con=session)
    for index, row in immo_df.iterrows():
        print(str(index + 1) + ". " + row['city'])
    # Zero price means, you have to ask the advertiser
    filter_price_zero = immo_df[immo_df['price'] > 0]

    # Calcualting min/max rest_budget for seats: 52 (100 %) to 65 (125 %)
    result = filter_price_zero.assign(min = lambda x: calc(x['price'], x['priceintervaltype'], x['totalfloorspace'], PLÄTZE_MAX),
                                      max = lambda x: calc(x['price'], x['priceintervaltype'], x['totalfloorspace'], PLÄTZE_MIN))

    print('city: ' + str(result['city']) +
          ' min_rest_budget: ' + str(result['min']) +
          ' max_rest_budget: ' + str(result['max']) +
          ' price: ' + str(result['price']) +
          ' totalfloorspace: ' + str(result['totalfloorspace']) +
          ' marketingtype: ' + str(result['marketingtype'])
          )
