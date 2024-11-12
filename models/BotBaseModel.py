from cassandra.cqlengine.models import Model

from config import DbConfig


class BotBaseModel(Model):
    __abstract__ = True
    __keyspace__ = DbConfig.DB_KEYSPACE

    @classmethod
    def set_keyspace(cls, keyspace):
        cls.__keyspace__ = keyspace
