import asyncio

from cassandra.cqlengine.management import sync_table

from config import DbConfig
from database.DbConnector import DbConnector
from models.UserMoneyByServer import UserMoneyByServer
from bot.utility import generate_objects_hash


class UserMoneyByServerRepository:
    def __init__(self, connector):
        self.connector = connector
        sync_table(UserMoneyByServer)

    def add_money(self, server_id, user_id, money_amount) -> None:
        server_hash = generate_objects_hash(server_id)
        user_id = str(user_id)
        records = UserMoneyByServer.objects(server_hash=server_hash, user_id=user_id).all()
        if records:
            record = records[0]
            record.user_money_amount += money_amount
            record.save()
        else:
            UserMoneyByServer.create(server_hash=server_hash, user_id=user_id, user_money_amount=money_amount)

    def subtract_money(self, server_id, user_id, money_amount) -> None:
        server_hash = generate_objects_hash(server_id)
        user_id = str(user_id)
        records = UserMoneyByServer.objects(server_hash=server_hash, user_id=user_id).all()
        if records:
            record = records[0]
            record.user_money_amount -= money_amount
            if record.user_money_amount < 0:
                record.user_money_amount = 0
            record.save()
        else:
            UserMoneyByServer.create(server_hash=server_hash, user_id=user_id, user_money_amount=0)

    def get_money(self, server_id, user_id) -> int:
        server_hash = generate_objects_hash(server_id)
        user_id = str(user_id)
        records = UserMoneyByServer.objects(server_hash=server_hash, user_id=user_id).all()
        if records:
            return records[0].user_money_amount
        else:
            return 0

    def get_ranking(self, server_id) -> list[tuple]:
        server_hash = generate_objects_hash(server_id)
        records = UserMoneyByServer.objects(server_hash=server_hash).all()
        records = sorted(records, key=lambda x: x.user_money_amount, reverse=True)
        return [(record.user_id, record.user_money_amount) for record in records]

    def delete_entry(self, server_id, user_id) -> None:
        server_hash = generate_objects_hash(server_id)
        user_id = str(user_id)
        records = UserMoneyByServer.objects(server_hash=server_hash, user_id=user_id).all()
        for record in records:
            record.delete()

    def clear_all_entries(self) -> None:
        records = UserMoneyByServer.objects.all()
        for record in records:
            record.delete()


async def main():
    db_connector = DbConnector(keyspace=DbConfig.DB_KEYSPACE, contact_points=DbConfig.DB_CONTACT_POINTS,
                               username=DbConfig.DB_USERNAME, password=DbConfig.DB_PASSWORD, port=DbConfig.DB_PORT)
    await db_connector.connect()
    repo = UserMoneyByServerRepository(db_connector)
    print(repo.get_money('123', '6969'))

    repo.add_money('123', '6969', 100)
    print(repo.get_money('123', '6969'))

    repo.subtract_money('123', '6969', 50)
    print(repo.get_money('123', '6969'))

    repo.add_money('123', '6969', 200)
    print(repo.get_money('123', '6969'))

    repo.delete_entry('123', '6969')
    print(repo.get_money('123', '6969'))


if __name__ == '__main__':
    asyncio.run(main())
