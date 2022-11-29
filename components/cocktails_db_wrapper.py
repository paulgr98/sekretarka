import requests


class CocktailsDB:
    def __init__(self):
        self.url = 'https://www.thecocktaildb.com/api/json/v1/1'

    def get_random_drink(self):
        return requests.get(self.url + '/random.php').json()

    def get_drink_by_name(self, name):
        return requests.get(self.url + '/search.php?s=' + name).json()

    def get_drink_by_id(self, drink_id):
        return requests.get(self.url + '/lookup.php?i=' + drink_id).json()

    def get_drink_by_ingredient(self, ingredient):
        return requests.get(self.url + '/filter.php?i=' + ingredient).json()

    def get_drink_by_letter(self, letter):
        return requests.get(self.url + '/search.php?f=' + letter).json()

    def get_drink_by_category(self, category):
        return requests.get(self.url + '/filter.php?c=' + category).json()

    def get_drink_by_glass(self, glass):
        return requests.get(self.url + '/filter.php?g=' + glass).json()

    def get_drink_by_alcoholic(self, alcoholic):
        return requests.get(self.url + '/filter.php?a=' + alcoholic).json()

    def get_category_list(self):
        return requests.get(self.url + '/list.php?c=list').json()

    def get_glass_list(self):
        return requests.get(self.url + '/list.php?g=list').json()

    def get_ingredient_list(self):
        return requests.get(self.url + '/list.php?i=list').json()

    def get_alcoholic_list(self):
        return requests.get(self.url + '/list.php?a=list').json()
