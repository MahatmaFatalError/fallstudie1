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


class RestaurantsSpider:

    def __init__(self, city):
        self.base_url = 'https://www.speisekarte.de'
        self.city = city
        self.helper = SpiderHelper()
        self.restaurant_urls = []
        self.restaurant_trees = []

    def run(self):
        self._scrape_restaurants()
        self._read_restaurant_urls()

        for restaurant_url in self.restaurant_urls:
            search_url = restaurant_url + '/speisekarte'
            restaurant_tree = self.helper.scrape_page(search_url)
            address = self.read_address(restaurant_tree)
            logger.info("Restaurant Address: {0}".format(address))
            menu_urls = self._get_menus(restaurant_tree)
            for menu_url in menu_urls:
                menu_tree = self.helper.scrape_page(menu_url)
                menu_items = self._get_menu_items(menu_tree)
                for item in menu_items:
                    logger.info(item)

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

    def _read_restaurant_urls(self):
        for tree in self.restaurant_trees:
            search_results = tree.xpath('//div[@class="search-result"]')
            for result in search_results:
                restaurant_url = result.get('target-link')
                self.restaurant_urls.append(restaurant_url)

    @staticmethod
    def _get_menu_items(tree):
        menu_items = tree.xpath('//div[@class="menu-entry-filter"]/div/div/p/span/text()')
        return menu_items

    @staticmethod
    def _get_menus(tree):
        menu_urls = tree.xpath('//div[@class="card no-border"]/div/div/a/@href')
        return menu_urls

    @staticmethod
    def read_address(tree):
        result = None
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
            result = json.dumps(address, ensure_ascii=False)

        return result


if __name__ == '__main__':
    util.setup_logging()

    city_name = 'mannheim'
    spider = RestaurantsSpider(city_name)
    helper = SpiderHelper()

    # tree = helper.scrape_page('https://www.speisekarte.de/mannheim/restaurant/friedrichsfelder_hof')
    # address = spider.read_address(tree)
    # print(address)

    spider.run()