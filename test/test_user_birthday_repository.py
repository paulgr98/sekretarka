import asyncio
import unittest

from config import DbConfig
from bot.database.DbConnector import DbConnector
from models.BotBaseModel import BotBaseModel
from repositories.UserBirthDayByServerRepository import UserBirthDayByServerRepository


class TestUserBirthdayRepository(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        test_keyspace = "sekretarka_test"
        cls.db_connector = DbConnector(keyspace=test_keyspace, contact_points=DbConfig.DB_CONTACT_POINTS,
                                       username=DbConfig.DB_USERNAME, password=DbConfig.DB_PASSWORD,
                                       port=DbConfig.DB_PORT)
        cls.claim_amount = 1000
        asyncio.run(cls.db_connector.connect())
        BotBaseModel.set_keyspace(test_keyspace)
        cls.birthday_repo = UserBirthDayByServerRepository(cls.db_connector)

    async def asyncSetUp(self):
        await self.cleanup()
        self.addCleanup(self.cleanup)

    async def test_add_birth_day(self):
        await self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = await self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        await self.birthday_repo.add_birthday("456", "111", "01.01.2000")
        birthday = await self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "01.01.2000")

    async def test_modify_birth_day(self):
        await self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = await self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        await self.birthday_repo.add_birthday("123", "111", "20.04.2005")
        birthday = await self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "20.04.2005")

        await self.birthday_repo.add_birthday("456", "111", "01.01.2000")
        birthday = await self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "01.01.2000")

    async def test_get_birthday_for_date(self):
        await self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        await self.birthday_repo.add_birthday("123", "222", "01.01.2005")
        await self.birthday_repo.add_birthday("456", "111", "05.01.2003")

        birthdays = await self.birthday_repo.get_birthday_for_date("123", "01.01.2000")
        self.assertEqual(birthdays, [("111", "01.01.2000"), ("222", "01.01.2005")])

        birthdays = await self.birthday_repo.get_birthday_for_date("456", "05.01.2003")
        self.assertEqual(birthdays, [("111", "05.01.2003")])

        birthdays = await self.birthday_repo.get_birthday_for_date("456", "01.01.2000")
        self.assertEqual(birthdays, [])

    async def test_delete_birth_day(self):
        await self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = await self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        await self.birthday_repo.add_birthday("123", "222", "01.01.2000")
        birthday = await self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "01.01.2000")

        await self.birthday_repo.add_birthday("456", "111", "05.01.2003")
        birthday = await self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "05.01.2003")

        result: bool = await self.birthday_repo.delete_user_on_server("123", "111")
        self.assertTrue(result)
        birthday = await self.birthday_repo.get_birthday("123", "111")
        self.assertIsNone(birthday)

        result = await self.birthday_repo.delete_user_on_server("123", "666")
        self.assertFalse(result)

        birthday = await self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "01.01.2000")

        birthday = await self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "05.01.2003")

    async def test_delete_user_on_all_servers(self):
        await self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = await self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        await self.birthday_repo.add_birthday("123", "222", "02.02.2005")
        birthday = await self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "02.02.2005")

        await self.birthday_repo.add_birthday("456", "111", "05.01.2003")
        birthday = await self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "05.01.2003")

        await self.birthday_repo.delete_user_on_all_servers("111")
        birthday = await self.birthday_repo.get_birthday("123", "111")
        self.assertIsNone(birthday)

        birthday = await self.birthday_repo.get_birthday("456", "111")
        self.assertIsNone(birthday)

        birthday = await self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "02.02.2005")

    async def cleanup(self):
        await self.birthday_repo.clear_all_entries()


if __name__ == '__main__':
    unittest.main()
