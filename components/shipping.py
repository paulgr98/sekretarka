from bot.database.DbConnector import DbConnector
from repositories.UserMatchesByServerRepository import UserMatchesByServerRepository


class ShippingService:
    def __init__(self, db_connector: DbConnector):
        self.match_repo = UserMatchesByServerRepository(db_connector)

    def save_users_match_for_today(self, guid_id, user_id, match_id):
        self.match_repo.add_today_match(guid_id, user_id, match_id)

    def get_users_match_for_today(self, guid_id, user_id):
        return self.match_repo.get_today_match(guid_id, user_id)
