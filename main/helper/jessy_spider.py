from lxml import html
import requests


class RestaurantsSpider:

    def __init__(self, base_url, city):
        self.base_url = base_url
        self.city = city

    def read_tree(self, url):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        return tree

    def fetch_restaurants(self):
        restaurant_url_template = '/{city_name}/restaurants'
        restaurant_urls = []

        search_url = self.base_url + restaurant_url_template.replace('{city_name}', self.city)
        tree = self.read_tree(search_url)
        search_results = tree.xpath('//div[@class="search-result"]')
        for result in search_results:
            restaurant_url = result.get('target-link')
            restaurant_urls.append(restaurant_url)
        return restaurant_urls

    def get_menus(self, restaurant_url):
        menu_category_urls = []
        search_url = restaurant_url + '/speisekarte'
        tree = self.read_tree(search_url)
        menu_cards = tree.xpath('//div[@class="card no-border"]')
        for card in menu_cards:
            category_url = card.xpath('//div[@class="text-uppercase text-primary"]/a/@href')
            menu_category_urls = category_url

        return menu_category_urls

    def get_menu_items(self, menu_url):
        tree = self.read_tree(menu_url)
        menu_items = tree.xpath('//div[@class="menu-entry-filter"]/div/div/p/span/text()')
        return menu_items


if __name__ == '__main__':
    city_name = 'mannheim'
    base_url = 'https://www.speisekarte.de'
    spider = RestaurantsSpider(base_url, city_name)

    restaurant_urls = spider.fetch_restaurants()

    for url in restaurant_urls:
        print('Restaurant URL: ' + url)
        menu_urls = spider.get_menus(url)
        for menu_url in menu_urls:
            print('Menü URL: ' + menu_url)
            menu_items = spider.get_menu_items(menu_url)
            for item in menu_items:
                print(item)