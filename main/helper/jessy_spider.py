from lxml import html
import requests
import logging

from main.helper import util
from main.helper.result import Result

logger = logging.getLogger(__name__)


class SpiderHelper:

    @staticmethod
    def scrape_page(page_url):
        tree = None
        logger.info('Scraping {0} ...'.format(page_url))
        request = requests.get(page_url)
        logger.info('Request Status Code: {0}'.format(request.status_code))
        if request.status_code == requests.codes.ok:
            tree = html.fromstring(request.content)
        else:
            logger.error(request.text)
        return tree

    @staticmethod
    def has_xpath(xpath, tree):
        result = False
        search_result = tree.xpath(xpath)
        if search_result:
            result = True
        return result


class SpeisekarteSpider:

    def __init__(self, city):
        self.base_url = 'https://www.speisekarte.de'
        self.city = city
        self.helper = SpiderHelper()
        self.restaurant_urls = []
        self.restaurant_trees = []
        self.menu_urls = []
        self.city_id = None
        self.result = Result()
        self.content = None

    def run(self):
        try:
            self._create_city_id()
            is_available = self._is_city_available()
            logger.debug(is_available)
            if is_available:
                logger.debug('City is available. Spider running for city {0}'.format(self.city))
                self._scrape_restaurants()
                self._scrape_restaurant_urls()
                self._scrape_menu_urls()
                self._build_menu_items()
                self.result.set_data(self.content)
                self.result.set_success(True)
            else:
                self.result.set_success(False)
                message = 'City {0} is not available'.format(self.city)
                self.result.set_message(message)
        except:
            self.result.set_success(False)
            # TODO Exceptions????

    def _create_city_id(self):
        self.city_id = self.city.lower().strip().replace(' ', '-')
        logger.debug('City ID: {0}'.format(self.city_id))

    def _is_city_available(self):
        has_fourzerofour = True
        city_url_template = '/{city_name}/restaurants'
        city_url = self.base_url + city_url_template.replace('{city_name}', self.city_id)
        tree = self.helper.scrape_page(city_url)
        if tree is not None:
            has_fourzerofour = self.helper.has_xpath('//div[@class="row mt-5 justify-content-center"]/div/h1/text()',
                                                     tree)
        return not has_fourzerofour

    def _build_menu_items(self):
        restaurants = []

        for urls in self.menu_urls:
            # all entries belonging to the same restaurant
            restaurant = {
                "id": None,
                "address": None,
                "categories": None,
                "services": None,
                "seats": None,
                "favourite_items": None,
                "menu": []
            }
            # get restaurant id
            first_restaurant_url = self.get_restaurant_url(urls[0])
            restaurant_tree = self.helper.scrape_page(first_restaurant_url)
            restaurant_id = self.read_restaurtant_id(first_restaurant_url)
            restaurant['id'] = restaurant_id
            # get categories
            categories = self.read_categories(restaurant_tree)
            if categories:
                restaurant['categories'] = categories
            # get services
            services = self.read_services(restaurant_tree)
            if services:
                restaurant['services'] = services
            # get seats
            seats = self.read_seats(restaurant_tree)
            if seats:
                restaurant['seats'] = seats
            # get favouritem items
            favourite_items = self.read_favourite_items(restaurant_tree)
            if favourite_items:
                restaurant['favourite_items'] = favourite_items
            for url in urls:
                menu_tree = self.helper.scrape_page(url)
                if menu_tree:
                    if not restaurant['address']:
                        address = self.read_address(menu_tree)
                        if address:
                            restaurant['address'] = address
                    menu_items = self.read_menu_items(menu_tree)
                    if menu_items:
                        category_id, category = self.read_menu_category(url)
                        menu_category = {
                            "id": category_id,
                            "category": category,
                            "menu_items": menu_items
                        }
                        restaurant['menu'].append(menu_category)

            restaurants.append(restaurant)

        all_restaurants = {
            "total": len(restaurants),
            "restaurants": restaurants
        }
        self.content = all_restaurants

    def get_result(self):
        return self.result

    def get_city_id(self):
        return self.city_id

    def _scrape_menu_urls(self):
        for restaurant_url in self.restaurant_urls:
            search_url = restaurant_url + '/speisekarte'
            restaurant_tree = self.helper.scrape_page(search_url)
            menu_urls = self.read_menus(restaurant_tree)
            if menu_urls:
                self.menu_urls.append(menu_urls)

    def _scrape_restaurants(self):
        restaurant_url_template = '/{city_name}/restaurants?page={page_number}'
        page_number = 1

        search_url = self.base_url + restaurant_url_template.format(city_name=self.city_id, page_number=page_number)
        tree = self.helper.scrape_page(search_url)
        while self.helper.has_xpath('//div[@class="search-result"]', tree):
            self.restaurant_trees.append(tree)
            page_number += 1
            search_url = self.base_url + restaurant_url_template.format(city_name=self.city_id, page_number=page_number)
            tree = self.helper.scrape_page(search_url)

    def _scrape_restaurant_urls(self):
        for tree in self.restaurant_trees:
            search_results = tree.xpath('//div[@class="search-result"]')
            for result in search_results:
                restaurant_url = result.get('target-link')
                self.restaurant_urls.append(restaurant_url)

    @staticmethod
    def read_favourite_items(tree):
        favourite_items = SpeisekarteSpider.read_menu_items(tree)
        cleaned_items = []
        search_string = 'finden'
        for item in favourite_items:
            if item.find(search_string) == -1:
                cleaned_items.append(item.strip())
        return cleaned_items

    @staticmethod
    def read_categories(tree):
        categories = tree.xpath('//a[@itemprop="servesCuisine"]/text()')
        cleaned_categories = []
        for cat in categories:
            cleaned_categories.append(cat.strip())
        return cleaned_categories

    @staticmethod
    def read_services(tree):
        categories = tree.xpath('//span[@class="badge badge-light mr-1 mb-1"]/text()')
        return categories

    @staticmethod
    def read_seats(tree):
        seats = []
        texts = tree.xpath('//div[@class="col-12 col-sm-6 col-md-4 mb-5"]/p[2]/text()')

        for text in texts:
            if text.find('Sitzplätze') != -1:
                seat = str(text).strip()
                seats.append(seat)

        return seats

    @staticmethod
    def get_restaurant_url(menu_url):
        return '/'.join(menu_url.split('/')[:-2])

    @staticmethod
    def read_menu_category(restaurant_url):
        logger.info('Reading Category from {0}'.format(restaurant_url))
        url_parts = restaurant_url.split('/')
        category_string = url_parts[7]
        category_parts = category_string.split('-')
        category_id = category_parts[0]
        category = category_parts[1]
        cleaned_category = category.replace('_', ' ')
        return category_id, cleaned_category.strip()

    @staticmethod
    def read_restaurtant_id(restaurant_url):
        url_parts = restaurant_url.split('/')
        restaurant_id = url_parts[5]
        return restaurant_id

    @staticmethod
    def read_menu_items(tree):
        items = []
        menu_items_span = tree.xpath('//div[@class="menu-entry-filter"]/div/div/span/text()')
        # menu_items_span_subtext = tree.xpath('//div[@class="menu-entry-filter"]/div/div/text()')
        menu_items_a = tree.xpath('//div[@class="menu-entry-filter"]/div/div/span/a/text()')
        for item_span in menu_items_span:
            text = item_span.strip()
            if text:
                items.append(text)
        for item_a in menu_items_a:
            text = item_a.strip()
            if text:
                items.append(text)
        # for span_subtext in menu_items_span_subtext:
        #     print('Subtext:')
        #     print(span_subtext.strip())

        return items

    @staticmethod
    def read_menus(tree):
        menu_urls = tree.xpath('//div[@class="card no-border"]/div/div/a/@href')
        return menu_urls

    @staticmethod
    def read_address(tree):
        address = {}

        name = tree.xpath('//p[@itemprop="name"]/text()')
        street = tree.xpath('//span[@itemprop="streetAddress"]/text()')
        zip_code = tree.xpath('//span[@itemprop="postalCode"]/text()')
        city = tree.xpath('//span[@itemprop="addressLocality"]/text()')

        if name and street and zip_code and city:
            address['name'] = name[0]
            address['street'] = street[0]
            address['zip_code'] = zip_code[0]
            address['city'] = city[0]

        return address


if __name__ == '__main__':
    util.setup_logging()

    city_name = 'berlin'
    spider = SpeisekarteSpider(city_name)
    helper = SpiderHelper()

    # tree = helper.scrape_page('https://www.speisekarte.de/mannheim/restaurant/friedrichsfelder_hof')
    # print(spider.read_favourite_items(tree))

    # spider.run()
    # result = spider.get_result()
    # print(result)