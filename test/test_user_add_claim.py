import asyncio
import unittest

from config import DbConfig
from bot.database.DbConnector import DbConnector
from models.BotBaseModel import BotBaseModel
from repositories.UserClaimsByServerRepository import UserClaimsByServerRepository
from repositories.UserMoneyByServerRepository import UserMoneyByServerRepository


class TestUserAddClaim(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_keyspace = "sekretarka_test"
        cls.db_connector = DbConnector(keyspace=test_keyspace, contact_points=DbConfig.DB_CONTACT_POINTS,
                                       username=DbConfig.DB_USERNAME, password=DbConfig.DB_PASSWORD,
                                       port=DbConfig.DB_PORT)
        cls.claim_amount = 1000
        asyncio.run(cls.db_connector.connect())
        BotBaseModel.set_keyspace(test_keyspace)
        cls.claim_repo = UserClaimsByServerRepository(cls.db_connector, cls.claim_amount)
        cls.money_repo = UserMoneyByServerRepository(cls.db_connector)

    def setUp(self):
        self.cleanup()
        self.addCleanup(self.cleanup)

    async def __async_test_add_claim__(self):
        claimed = self.claim_repo.try_add_claim("123", "111")
        user_money = self.money_repo.get_money("123", "111")
        self.assertTrue(claimed)
        self.assertEqual(user_money, self.claim_amount)

        claimed = self.claim_repo.try_add_claim("123", "111")
        user_money = self.money_repo.get_money("123", "111")
        self.assertFalse(claimed)
        self.assertEqual(user_money, self.claim_amount)

        claimed = self.claim_repo.try_add_claim("123", "222")
        user_money = self.money_repo.get_money("123", "222")
        self.assertTrue(claimed)
        self.assertEqual(user_money, self.claim_amount)

        claimed = self.claim_repo.try_add_claim("456", "111")
        user_money = self.money_repo.get_money("456", "111")
        self.assertTrue(claimed)
        self.assertEqual(user_money, self.claim_amount)

        claimed = self.claim_repo.try_add_claim("456", "222")
        user_money = self.money_repo.get_money("456", "222")
        self.assertTrue(claimed)
        self.assertEqual(user_money, self.claim_amount)

    def test_add_claim(self):
        asyncio.run(self.__async_test_add_claim__())

    def cleanup(self):
        self.claim_repo.clear_all_entries()
        self.money_repo.clear_all_entries()


if __name__ == '__main__':
    unittest.main()
