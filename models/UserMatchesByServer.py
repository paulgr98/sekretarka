from cassandra.cqlengine.columns import Text
from cassandra.cqlengine.models import Model


class UserMatchesByServer(Model):
    __keyspace__ = 'sekretarka'
    server_date_hash = Text(primary_key=True, partition_key=True)
    user_id = Text(primary_key=True)
    user_match_id = Text()
