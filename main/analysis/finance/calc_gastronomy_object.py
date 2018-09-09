# coding=utf-8

from config import constants
import pandas as pd


def calc(price, priceintervaltype, totalfloorspace, seats):
    if 'ONE_TIME_CHARGE' in str(priceintervaltype):
        multiplier = constants.BUY_FACTOR
    else:
        multiplier = constants.RENT_FACTOR
    rest_budget = constants.BUDGET - price * multiplier - constants.FURNISH_COST_PER_SQUARE_METER * totalfloorspace - seats * constants.FURNISH_COST_PER_SEAT
    return rest_budget


if __name__ == '__main__':
    from main.helper.db_helper import SqlHelper

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    session = db.get_connection()
    immo_df = pd.read_sql_table(table_name=constants.SQL_TABLE_IMMOSCOUT, con=session)
    for index, row in immo_df.iterrows():
        print(str(index + 1) + ". " + row['city'])
    # Zero price means, you have to ask the advertiser
    filter_price_zero = immo_df[immo_df['price'] >= 0]

    # Calcualting min/max rest_budget for seats: 52 (100 %) to 65 (125 %)
    result = filter_price_zero.assign(min = lambda x: calc(x['price'], x['priceintervaltype'], x['totalfloorspace'], constants.SEATS_MAX),
                                      max = lambda x: calc(x['price'], x['priceintervaltype'], x['totalfloorspace'], constants.SEATS_MIN))

    result = result[result['min'] >= 0]

    print('city: ' + str(result['city']) +
          ' min_rest_budget: ' + str(result['min']) +
          ' max_rest_budget: ' + str(result['max']) +
          ' price: ' + str(result['price']) +
          ' totalfloorspace: ' + str(result['totalfloorspace']) +
          ' marketingtype: ' + str(result['marketingtype'])
          )

    result.to_sql('immsoscout_buy', con=session, if_exists='replace', index=False)
