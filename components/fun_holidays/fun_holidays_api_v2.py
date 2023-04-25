import datetime as dt
import json


class FunHolidaysApi(object):
    def __init__(self):
        self.holiday_file = 'components/fun_holidays/holidays.json'

    def get_holidays_for_date(self, month: int, day: int) -> list[str]:
        with open(self.holiday_file, 'r', encoding='utf-8') as f:
            data_raw = f.read()
        data_json = json.loads(data_raw)
        names = []
        for holiday in data_json:
            if holiday['month'] == month and holiday['day'] == day:
                names.append(holiday['name'])
        return names

    def get_holidays_for_today(self) -> list[str]:
        now = dt.datetime.now()
        month_number = now.month
        day_number = now.day
        return self.get_holidays_for_date(month_number, day_number)


if __name__ == '__main__':
    api = FunHolidaysApi()
    print(api.get_holidays_for_today())
