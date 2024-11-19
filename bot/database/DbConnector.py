import asyncio

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.cqlengine import connection

from config import DbConfig
from bot.logger import logger


class DbConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DbConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, contact_points=None, keyspace=None, username=None, password=None, port=None):
        if self._initialized:
            return
        if contact_points is None:
            contact_points = ['127.0.0.1']
        self.contact_points = contact_points
        self.keyspace = keyspace
        self.auth_provider = PlainTextAuthProvider(username=username,
                                                   password=password) if username and password else None
        self.port = port if port else 9042
        self.cluster = Cluster(contact_points=self.contact_points, auth_provider=self.auth_provider, port=self.port)
        self.session = None
        self._initialized = True

    async def connect(self):
        if self.session is None:
            try:
                self.session = self.cluster.connect()
                if self.keyspace:
                    self.session.set_keyspace(self.keyspace)
                connection.register_connection('default', session=self.session)
                connection.set_default_connection('default')
                print("DB connection successful")
            except Exception as e:
                print(f"DB connection failed: {e}")
                self.session = None


async def main():
    db_connector = DbConnector(keyspace=DbConfig.DB_KEYSPACE, contact_points=DbConfig.DB_CONTACT_POINTS,
                               username=DbConfig.DB_USERNAME, password=DbConfig.DB_PASSWORD, port=DbConfig.DB_PORT)
    await db_connector.connect()


if __name__ == '__main__':
    asyncio.run(main())
