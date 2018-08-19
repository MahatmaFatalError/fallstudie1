import json
import logging
import pandas as pd
from main.helper import util

logger = logging.getLogger(__name__)

data_excerpt = []


def run(filename):
    create_excerpt(filename)
    df = pd.DataFrame.from_dict(data_excerpt, orient='columns')
    print(df.describe())


def create_excerpt(filename):
    with open(filename) as file:
        for index, line in enumerate(file):
            if index == 5:
                break
            else:
                data_excerpt.append(line)
        file.close()


if __name__ == '__main__':
    util.setup_logging()

    academic_file = 'yelp_academic_dataset_review.json'
    run(academic_file)
