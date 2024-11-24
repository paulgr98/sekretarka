import requests


class MealDB:
    def __init__(self):
        self.url = 'https://www.themealdb.com/api/json/v1/1'

    def get_random_meal(self) -> dict:
        return requests.get(self.url + '/random.php').json()['meals'][0]

    def get_meal_by_name(self, name: str) -> dict:
        return requests.get(self.url + '/search.php?s=' + name).json()['meals'][0]

    def get_meal_by_id(self, meal_id):
        return requests.get(self.url + '/lookup.php?i=' + meal_id).json()['meals'][0]

    def list_categories(self) -> list:
        list_categories: list[dict] = requests.get(self.url + '/list.php?c=list').json()['meals']
        return [category['strCategory'] for category in list_categories]

    def list_areas(self) -> list:
        list_areas: list[dict] = requests.get(self.url + '/list.php?a=list').json()['meals']
        return [area['strArea'] for area in list_areas]

    def filter_by_category(self, category: str) -> list:
        return requests.get(self.url + '/filter.php?c=' + category).json()['meals']

    def filter_by_area(self, area: str) -> list:
        return requests.get(self.url + '/filter.php?a=' + area).json()['meals']

    def filter_by_ingredient(self, ingredient: str) -> list:
        return requests.get(self.url + '/filter.php?i=' + ingredient).json()['meals']



