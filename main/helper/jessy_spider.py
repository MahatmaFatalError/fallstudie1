from lxml import html
import requests
import logging
import json

from main.helper import util

logger = logging.getLogger(__name__)


class SpiderHelper:

    @staticmethod
    def scrape_page(page_url):
        logger.info('Scraping {0} ...'.format(page_url))
        page = requests.get(page_url)
        tree = html.fromstring(page.content)
        return tree

    @staticmethod
    def has_xpath(xpath, tree):
        result = False
        search_result = tree.xpath(xpath)
        if search_result:
            result = True
        return result


class RestaurantSpider:

    def __init__(self, city):
        self.base_url = 'https://www.speisekarte.de'
        self.city = city
        self.helper = SpiderHelper()
        self.restaurant_urls = []
        self.restaurant_trees = []
        self.menu_urls = []

    def run(self):
        self._scrape_restaurants()
        self._scrape_restaurant_urls()
        self._scrape_menu_urls()
        self._build_menu_items_json()

    def _build_menu_items_json(self):
        restaurants = []

        for urls in self.menu_urls:
            restaurant = {
                'id': None,
                'address': None,
                'menu': []
            }
            for url in urls:
                if not restaurant['id']:
                    restaurant_id = self.read_restaurtant_id(url)
                    restaurant['id'] = restaurant_id
                menu_tree = self.helper.scrape_page(url)
                if not restaurant['address']:
                    address = self.read_address(menu_tree)
                    if address:
                        restaurant['address'] = address
                menu_items = self.read_menu_items(menu_tree)
                if menu_items:
                    category_id, category = self.read_menu_category(url)
                    menu_category = {
                        'id': category_id,
                        'category': category,
                        'menu_items': menu_items
                    }
                    restaurant['menu'].append(menu_category)

            restaurants.append(restaurant)

        all_restaurants = {
            'total': len(restaurants),
            'restaurants': restaurants
        }
        self.result = all_restaurants

    def get_result_as_json(self):
        print(self.result)
        return json.dumps(self.result, ensure_ascii=False)

    def get_result(self):
        return self.result

    def _scrape_menu_urls(self):
        for restaurant_url in self.restaurant_urls:
            search_url = restaurant_url + '/speisekarte'
            restaurant_tree = self.helper.scrape_page(search_url)
            menu_urls = self.get_menus(restaurant_tree)
            if menu_urls:
                self.menu_urls.append(menu_urls)

    def _scrape_restaurants(self):
        restaurant_url_template = '/{city_name}/restaurants?page={page_number}'
        page_number = 1

        search_url = self.base_url + restaurant_url_template.format(city_name=self.city, page_number=page_number)
        tree = self.helper.scrape_page(search_url)
        while self.helper.has_xpath('//div[@class="search-result"]', tree):
            self.restaurant_trees.append(tree)
            page_number += 1
            search_url = self.base_url + restaurant_url_template.format(city_name=self.city, page_number=page_number)
            tree = self.helper.scrape_page(search_url)

    def _scrape_restaurant_urls(self):
        for tree in self.restaurant_trees:
            search_results = tree.xpath('//div[@class="search-result"]')
            for result in search_results:
                restaurant_url = result.get('target-link')
                self.restaurant_urls.append(restaurant_url)

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
        menu_items = tree.xpath('//div[@class="menu-entry-filter"]/div/div/span/text()')
        for item in menu_items:
            if item:
                items.append(item.strip())
        return items

    @staticmethod
    def get_menus(tree):
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

    city_name = 'schopfheim'
    spider = RestaurantSpider(city_name)
    helper = SpiderHelper()

    # tree = helper.scrape_page('https://www.speisekarte.de/schopfheim/restaurant/restaurant_hermes/speisekarte/1483436-vorspeisen_kalt_und_warm')
    # print(spider.read_menu_items(tree))

    spider.run()
    result = spider.get_result_as_json()
    print(result)