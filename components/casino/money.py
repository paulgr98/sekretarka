from database.DbConnector import DbConnector
from repositories.UserClaimsByServerRepository import UserClaimsByServerRepository
from repositories.UserMoneyByServerRepository import UserMoneyByServerRepository


class MoneyService:
    def __init__(self, db_connector: DbConnector, default_daily_claim_amount: int = 1000):
        self.default_daily_claim_amount = default_daily_claim_amount
        self.money_repo = UserMoneyByServerRepository(db_connector)
        self.claims_repo = UserClaimsByServerRepository(db_connector,
                                                        default_claim_amount=self.default_daily_claim_amount)

    def get_money(self, server_id, user_id) -> int:
        return self.money_repo.get_money(server_id, user_id)

    def add_money(self, server_id, user_id, money_amount) -> None:
        self.money_repo.add_money(server_id, user_id, money_amount)

    def subtract_money(self, server_id, user_id, money_amount) -> None:
        self.money_repo.subtract_money(server_id, user_id, money_amount)

    def get_ranking(self, server_id) -> list:
        return self.money_repo.get_ranking(server_id)

    def try_add_claim(self, server_id, user_id) -> bool:
        return self.claims_repo.try_add_claim(server_id, user_id)
