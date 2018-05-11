import argparse
import config
from YelpHelper import YelpHelper
import sys

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--location', dest='location',
                        default='Heidelberg, DE', type=str,
                        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        yelper = YelpHelper(config.YELP_API_KEY)
        yelper.query_api(input_values.location)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()