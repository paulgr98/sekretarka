from datetime import datetime
from typing import Optional

from cassandra.cqlengine.management import sync_table
from cassandra.util import Date

from models.UserBirthDayByServer import UserBirthDayByServer
from bot.utility import generate_objects_hash


def __format_date__(original_date: str, original_date_format: str, result_date_format) -> str:
    date_obj = datetime.strptime(original_date, original_date_format)
    formatted = date_obj.strftime(result_date_format)
    return formatted


class UserBirthDayByServerRepository:
    def __init__(self, connector):
        self.connector = connector
        self.user_date_format = "%d.%m.%Y"
        self.server_date_format = "%Y-%m-%d"
        sync_table(UserBirthDayByServer)

    def add_birthday(self, server_id, user_id, birth_day) -> None:
        server_hash = generate_objects_hash(server_id, include_date=False)
        user_id = str(user_id)
        birth_day = __format_date__(birth_day, self.user_date_format, self.server_date_format)
        records = UserBirthDayByServer.objects(server_hash=server_hash, user_id=user_id).all()
        if records:
            record = records[0]
            record.user_birth_day = birth_day
            record.save()
        else:
            UserBirthDayByServer.create(server_hash=server_hash, user_id=user_id, user_birth_day=birth_day)

    def get_birthday(self, server_id, user_id) -> Optional[str]:
        server_hash = generate_objects_hash(server_id, include_date=False)
        user_id = str(user_id)
        records = UserBirthDayByServer.objects(server_hash=server_hash, user_id=user_id).all()
        if records:
            server_format_data: Date = records[0].user_birth_day
            return server_format_data.date().strftime(self.user_date_format)
        else:
            return None

    def get_birthday_for_date(self, server_id, date) -> list[tuple]:
        server_hash = generate_objects_hash(server_id, include_date=False)
        date_obj = datetime.strptime(date, self.user_date_format)
        day = date_obj.day
        month = date_obj.month
        records = UserBirthDayByServer.objects(server_hash=server_hash).all()
        result = []
        for record in records:
            if record.user_birth_day.date().day == day and record.user_birth_day.date().month == month:
                result.append((record.user_id, record.user_birth_day.date().strftime(self.user_date_format)))
        return result

    def delete_user_on_server(self, server_id, user_id) -> bool:
        server_hash = generate_objects_hash(server_id, include_date=False)
        user_id = str(user_id)
        records = UserBirthDayByServer.objects(server_hash=server_hash, user_id=user_id).all()
        for record in records:
            record.delete()
        return len(records) > 0

    def delete_user_on_all_servers(self, user_id) -> None:
        user_id = str(user_id)
        records = UserBirthDayByServer.objects(user_id=user_id).all()
        for record in records:
            record.delete()

    def get_all_birthdays_on_server(self, server_id) -> list[tuple]:
        server_hash = generate_objects_hash(server_id, include_date=False)
        records = UserBirthDayByServer.objects(server_hash=server_hash).all()
        return [(record.user_id, record.user_birth_day.date().strftime(self.user_date_format)) for record in records]

    def clear_all_entries(self) -> None:
        records = UserBirthDayByServer.objects.all()
        for record in records:
            record.delete()
