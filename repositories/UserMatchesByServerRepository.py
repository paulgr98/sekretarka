import asyncio
import datetime as dt

from cassandra.cqlengine.management import sync_table

from config import DbConfig
from database.DbConnector import DbConnector
from models.UserMatchesByServer import UserMatchesByServer
from utility import generate_objects_hash


class UserMatchesByServerRepository:
    def __init__(self, connector):
        self.connector = connector
        sync_table(UserMatchesByServer)

    def add_today_match(self, server_id, user_id, matched_user_id):
        server_date_hash = generate_objects_hash(server_id, include_date=True)
        user_id = str(user_id)
        matched_user_id = str(matched_user_id)
        records = UserMatchesByServer.objects(server_date_hash=server_date_hash).all()
        if not any(record.user_id == user_id for record in records):
            UserMatchesByServer.create(server_date_hash=server_date_hash, user_id=user_id,
                                       user_match_id=matched_user_id)

    def get_today_matches(self, server_id):
        server_date_hash = generate_objects_hash(server_id, include_date=True)
        records = UserMatchesByServer.objects(server_date_hash=server_date_hash).all()
        return {record.user_id: record.user_match_id for record in records} if records else None

    def get_matches_at_date(self, server_id, date: dt.datetime):
        server_date_hash = generate_objects_hash(server_id, include_date=True, date=date)
        records = UserMatchesByServer.objects(server_date_hash=server_date_hash).all()
        return {record.user_id: record.user_match_id for record in records} if records else None

    def get_today_match(self, server_id, user_id):
        server_date_hash = generate_objects_hash(server_id, include_date=True)
        user_id = str(user_id)
        records = UserMatchesByServer.objects(server_date_hash=server_date_hash).all()
        for record in records:
            if record.user_id == user_id:
                return record.user_match_id
        return None

    def get_match_at_date(self, server_id, user_id, date: dt.datetime):
        server_date_hash = generate_objects_hash(server_id, include_date=True, date=date)
        user_id = str(user_id)
        records = UserMatchesByServer.objects(server_date_hash=server_date_hash).all()
        for record in records:
            if record.user_id == user_id:
                return record.user_match_id
        return None

    def delete_today_match(self, server_id, user_id):
        server_date_hash = generate_objects_hash(server_id, include_date=True)
        user_id = str(user_id)
        records = UserMatchesByServer.objects(server_date_hash=server_date_hash).all()
        for record in records:
            if record.user_id == user_id:
                record.delete()
                break


async def main():
    db_connector = DbConnector(keyspace=DbConfig.DB_KEYSPACE, contact_points=DbConfig.DB_CONTACT_POINTS,
                               username=DbConfig.DB_USERNAME, password=DbConfig.DB_PASSWORD, port=DbConfig.DB_PORT)
    await db_connector.connect()
    repo = UserMatchesByServerRepository(db_connector)
    repo.add_today_match("123", "111", "222")
    repo.add_today_match("123", "111", "333")
    repo.add_today_match("123", "666", "999")
    print(repo.get_today_matches("123"))
    print(repo.get_today_match("123", "111"))
    print(repo.get_today_match("123", "666"))
    repo.delete_today_match("123", "111")
    print(repo.get_today_matches("123"))
    repo.delete_today_match("123", "666")
    print(repo.get_today_matches("123"))


if __name__ == '__main__':
    asyncio.run(main())
