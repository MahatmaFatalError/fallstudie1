import json
import logging
import pandas as pd
from main.helper import util

logger = logging.getLogger(__name__)


def run(filename):
    with open(filename) as fd:
        for line in fd:
            json_string = '[' + line + ']'
            json_dict = json.loads(json_string)
            df = pd.DataFrame.from_dict(json_dict, orient='columns')
            print(df['text'])


if __name__ == '__main__':
    util.setup_logging()

    academic_file = 'yelp_academic_dataset_review.json'
    run(academic_file)
