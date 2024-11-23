import datetime as dt
import pytz


def get_next_race():
    today = dt.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    time_added_quali = dt.timedelta(minutes=11)
    time_added_race = dt.timedelta(minutes=12)
    quali_time_str = (today + time_added_quali).strftime('%H:%M:%S')
    race_time_str = (today + time_added_race).strftime('%H:%M:%S')
    year_str = today.strftime('%Y')
    race_json = f'''{{
       "season": "{year_str}",
       "round": "69",
       "raceName": "Test GP",
       "Circuit": {{
           "circuitName": "Test Circuit"
       }},
       "date": "{date_str}",
       "time": "{race_time_str}",
       "Qualifying": {{
            "date": "{date_str}",
            "time": "{quali_time_str}"
    }}
   }}'''

    return race_json


def get_time(delay: int):
    notification_time = 15
    now = dt.datetime.now()
    localized_now = pytz.timezone('Europe/Warsaw').localize(now)
    target = localized_now + dt.timedelta(minutes=notification_time)
    target += dt.timedelta(minutes=delay)
    return target


def get_race_time() -> dt.datetime:
    return get_time(delay=2)


def get_qualification_time() -> dt.datetime:
    return get_time(delay=1)


def main():
    race_json = get_next_race()
    print(race_json)


if __name__ == '__main__':
    main()
