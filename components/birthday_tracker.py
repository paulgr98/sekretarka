import json
import datetime as dt
import os


class BirthdayTracker(object):
    def __init__(self):
        self.file_path = 'data/birthdays.json'
        self.birthdays = self._load_birthdays()

    def _load_birthdays(self) -> dict[str, str]:
        if os.path.exists(self.file_path):
            # if file exists, but has no json data
            if os.stat(self.file_path).st_size == 0:
                self._save_empty_dict()
            with open(self.file_path, 'r') as f:
                birthdays = json.load(f)
            return birthdays
        else:
            # create path if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self._save_empty_dict()
            return {}

    def _save_empty_dict(self) -> None:
        with open(self.file_path, 'w') as f:
            json.dump({}, f, indent=4)

    def _save_birthdays(self) -> None:
        with open(self.file_path, 'w') as f:
            json.dump(self.birthdays, f, indent=4)

    def add_birthday(self, user_id: str, date: str) -> None:
        if str(user_id) in self.birthdays:
            del self.birthdays[str(user_id)]
        self.birthdays[user_id] = date
        self._save_birthdays()

    def remove_birthday(self, user_id: str) -> None:
        if str(user_id) not in self.birthdays:
            raise IndexError('Użytkownik nie ma ustawionych urodzin')
        del self.birthdays[str(user_id)]
        self._save_birthdays()

    def get_birthday_by_id(self, user_id: str) -> str or None:
        if str(user_id) not in self.birthdays:
            return None
        return self.birthdays[str(user_id)]

    def get_birthdays_by_date(self, date: str) -> list[tuple[str, str]]:
        date_dt = dt.datetime.strptime(date, '%d.%m.%Y')
        result = []
        for user_id, birthday in self.birthdays.items():
            birthday_dt = dt.datetime.strptime(birthday, '%d.%m.%Y')
            if birthday_dt.day == date_dt.day and birthday_dt.month == date_dt.month:
                result.append((user_id, birthday))
        return result

    def get_all_birthdays(self) -> dict[str, str]:
        return self.birthdays

    def get_nearest_upcoming_birthdays(self) -> list[tuple[str, str]]:
        """
        Finds the nearest upcoming birthdays between today and the end of the year
        """
        today = dt.datetime.today()
        nearest_birthday_date = None
        # find the nearest upcoming birthday date
        for user_id, birthday in self.birthdays.items():
            birthday_date = dt.datetime.strptime(birthday, '%d.%m.%Y')
            # ignore the year
            birthday_date = birthday_date.replace(year=today.year)
            if birthday_date < today:
                continue
            # if nearest_birthday_date is already set, compare it use the version with current year
            nearest_bday_no_year = None
            if nearest_birthday_date is not None:
                nearest_bday_no_year = dt.datetime.strptime(nearest_birthday_date, '%d.%m.%Y').replace(year=today.year)
            # if nearest_birthday_date is not yet set or the current birthday is closer than the previous one
            if nearest_birthday_date is None or birthday_date < nearest_bday_no_year:
                nearest_birthday_date = birthday

        # if there are no upcoming birthdays, return empty list
        if nearest_birthday_date is None:
            return []

        # find all birthdays with the nearest date
        result = self.get_birthdays_by_date(nearest_birthday_date)
        return result

