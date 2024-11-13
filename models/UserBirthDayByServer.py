from cassandra.cqlengine.columns import Date, Text

from models.BotBaseModel import BotBaseModel


class UserBirthDayByServer(BotBaseModel):
    server_hash = Text(primary_key=True, partition_key=True)
    user_id = Text(primary_key=True, index=True)
    user_birth_day = Date() # format: YYYY-MM-DD
