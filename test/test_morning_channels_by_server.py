import asyncio
import unittest

from bot.database.DbConnector import DbConnector
from config import DbConfig
from models.BotBaseModel import BotBaseModel
from repositories.MorningChannelsByServerRepository import MorningChannelsByServerRepository


class TestMorningChannelsByServerRepository(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        test_keyspace = "sekretarka_test"
        cls.db_connector = DbConnector(keyspace=test_keyspace, contact_points=DbConfig.DB_CONTACT_POINTS,
                                       username=DbConfig.DB_USERNAME, password=DbConfig.DB_PASSWORD,
                                       port=DbConfig.DB_PORT)
        asyncio.run(cls.db_connector.connect())
        BotBaseModel.set_keyspace(test_keyspace)
        cls.repo = MorningChannelsByServerRepository(cls.db_connector)

    async def asyncSetUp(self):
        await self.cleanup()
        self.addCleanup(self.cleanup)

    async def test_add_channel(self):
        await self.repo.add_channel('123', '666')
        self.assertEqual(await self.repo.get_channels('123'), ['666'])

        await self.repo.add_channel('123', '777')
        self.assertEqual(await self.repo.get_channels('123'), ['666', '777'])

        await self.repo.add_channel('123', '666')
        self.assertEqual(await self.repo.get_channels('123'), ['666', '777'])

        await self.repo.add_channel('456', '666')
        self.assertEqual(await self.repo.get_channels('123'), ['666', '777'])
        self.assertEqual(await self.repo.get_channels('456'), ['666'])

        await self.repo.add_channel('456', '777')
        self.assertEqual(await self.repo.get_channels('123'), ['666', '777'])
        self.assertEqual(await self.repo.get_channels('456'), ['666', '777'])

    async def test_remove_channel(self):
        await self.repo.add_channel('123', '666')
        await self.repo.add_channel('123', '777')
        await self.repo.add_channel('456', '666')
        await self.repo.add_channel('456', '777')

        await self.repo.remove_channel('123', '666')
        self.assertEqual(await self.repo.get_channels('123'), ['777'])
        self.assertEqual(await self.repo.get_channels('456'), ['666', '777'])

        await self.repo.remove_channel('456', '777')
        self.assertEqual(await self.repo.get_channels('123'), ['777'])
        self.assertEqual(await self.repo.get_channels('456'), ['666'])

    async def cleanup(self):
        await self.repo.clear_all_entries()
