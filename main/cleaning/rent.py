import logging
import numpy

from config import constants
from main.database.db_helper import SqlHelper
from main.database.init_db import RentAvgCalculated
from main.helper import util

logger = logging.getLogger(__name__)


def main():
    rents = []
    util.setup_logging()

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    db.create_session()

    result = db.fetch_entity_where('City', True, True, rent_avg=None)

    for city in result:
        rents.append(city.rent_avg)

    rent_avg = int(numpy.mean(rents))

    result = db.fetch_entity_where('City', True, False, rent_avg=None)

    for city in result:
        rent_avg_calculated = RentAvgCalculated()
        rent_avg_calculated.city_id = city.id
        rent_avg_calculated.rent_avg = rent_avg
        db.insert(rent_avg_calculated)

    db.commit_session()
    db.close_session()


if __name__ == '__main__':
    main()