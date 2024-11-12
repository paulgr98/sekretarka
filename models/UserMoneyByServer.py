from cassandra.cqlengine.columns import Integer, Text

from models.BotBaseModel import BotBaseModel


class UserMoneyByServer(BotBaseModel):
    server_hash = Text(primary_key=True, partition_key=True)
    user_id = Text(primary_key=True)
    user_money_amount = Integer()
