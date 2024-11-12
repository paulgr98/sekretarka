from cassandra.cqlengine.columns import Integer, Text

from models.BotBaseModel import BotBaseModel


class UserClaimsByServer(BotBaseModel):
    server_date_hash = Text(primary_key=True, partition_key=True)
    user_id = Text(primary_key=True)
    user_claim_amount = Integer()
