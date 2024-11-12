import datetime as dt

import requests

@DeprecationWarning
class FunHolidaysApi(object):
    def __init__(self):
        self.url = "https://pniedzwiedzinski.github.io/kalendarz-swiat-nietypowych/"

    def get_holidays_for_date(self, month: int, day: int) -> list[str]:
        response = requests.get(f'{self.url}{month}/{day}.json')
        response_json = response.json()
        names = [holiday['name'] for holiday in response_json]
        return names

    def get_holidays_for_today(self) -> list[str]:
        now = dt.datetime.now()
        month_number = now.month
        day_number = now.day
        return self.get_holidays_for_date(month_number, day_number)
