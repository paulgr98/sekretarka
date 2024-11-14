import asyncio
import unittest

from config import DbConfig
from bot.database.DbConnector import DbConnector
from models.BotBaseModel import BotBaseModel
from repositories.UserBirthDayByServerRepository import UserBirthDayByServerRepository


class TestUserBirthdayRepository(unittest.TestCase):
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

    def setUp(self):
        self.cleanup()
        self.addCleanup(self.cleanup)

    def test_add_birth_day(self):
        self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        self.birthday_repo.add_birthday("456", "111", "01.01.2000")
        birthday = self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "01.01.2000")

    def test_modify_birth_day(self):
        self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        self.birthday_repo.add_birthday("123", "111", "20.04.2005")
        birthday = self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "20.04.2005")

        self.birthday_repo.add_birthday("456", "111", "01.01.2000")
        birthday = self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "01.01.2000")

    def test_get_birthday_for_date(self):
        self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        self.birthday_repo.add_birthday("123", "222", "01.01.2005")
        self.birthday_repo.add_birthday("456", "111", "05.01.2003")

        birthdays = self.birthday_repo.get_birthday_for_date("123", "01.01.2000")
        self.assertEqual(birthdays, [("111", "01.01.2000"), ("222", "01.01.2005")])

        birthdays = self.birthday_repo.get_birthday_for_date("456", "05.01.2003")
        self.assertEqual(birthdays, [("111", "05.01.2003")])

        birthdays = self.birthday_repo.get_birthday_for_date("456", "01.01.2000")
        self.assertEqual(birthdays, [])

    def test_delete_birth_day(self):
        self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        self.birthday_repo.add_birthday("123", "222", "01.01.2000")
        birthday = self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "01.01.2000")

        self.birthday_repo.add_birthday("456", "111", "05.01.2003")
        birthday = self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "05.01.2003")

        result: bool = self.birthday_repo.delete_user_on_server("123", "111")
        self.assertTrue(result)
        birthday = self.birthday_repo.get_birthday("123", "111")
        self.assertIsNone(birthday)

        result = self.birthday_repo.delete_user_on_server("123", "666")
        self.assertFalse(result)

        birthday = self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "01.01.2000")

        birthday = self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "05.01.2003")

    def test_delete_user_on_all_servers(self):
        self.birthday_repo.add_birthday("123", "111", "01.01.2000")
        birthday = self.birthday_repo.get_birthday("123", "111")
        self.assertEqual(birthday, "01.01.2000")

        self.birthday_repo.add_birthday("123", "222", "02.02.2005")
        birthday = self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "02.02.2005")

        self.birthday_repo.add_birthday("456", "111", "05.01.2003")
        birthday = self.birthday_repo.get_birthday("456", "111")
        self.assertEqual(birthday, "05.01.2003")

        self.birthday_repo.delete_user_on_all_servers("111")
        birthday = self.birthday_repo.get_birthday("123", "111")
        self.assertIsNone(birthday)

        birthday = self.birthday_repo.get_birthday("456", "111")
        self.assertIsNone(birthday)

        birthday = self.birthday_repo.get_birthday("123", "222")
        self.assertEqual(birthday, "02.02.2005")

    def cleanup(self):
        self.birthday_repo.clear_all_entries()


if __name__ == '__main__':
    unittest.main()
