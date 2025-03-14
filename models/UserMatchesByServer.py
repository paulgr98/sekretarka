from cassandra.cqlengine.columns import Text

from models.BotBaseModel import BotBaseModel


class UserMatchesByServer(BotBaseModel):
    server_date_hash = Text(primary_key=True, partition_key=True)
    user_id = Text(primary_key=True)
    user_match_id = Text()
