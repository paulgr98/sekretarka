from cassandra.cqlengine.columns import Date, Text

from models.BotBaseModel import BotBaseModel


class MorningChannelsByServer(BotBaseModel):
    server_hash = Text(primary_key=True, partition_key=True)
    channel_id = Text(primary_key=True)
