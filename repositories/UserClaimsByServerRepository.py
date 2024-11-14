from cassandra.cqlengine.management import sync_table

from repositories.UserMoneyByServerRepository import UserMoneyByServerRepository
from models.UserClaimsByServer import UserClaimsByServer
from bot.utility import generate_objects_hash


class UserClaimsByServerRepository:
    def __init__(self, connector, default_claim_amount: int):
        self.connector = connector
        self.default_claim_amount = default_claim_amount
        self.money_repo = UserMoneyByServerRepository(connector)
        sync_table(UserClaimsByServer)

    def try_add_claim(self, server_id, user_id) -> bool:
        server_date_hash = generate_objects_hash(server_id, include_date=True)
        user_id = str(user_id)
        records = UserClaimsByServer.objects(server_date_hash=server_date_hash, user_id=user_id).all()
        if records:
            return False
        else:
            UserClaimsByServer.create(server_date_hash=server_date_hash,
                                      user_id=user_id, user_claim_amount=self.default_claim_amount)
            self.money_repo.add_money(server_id, user_id, self.default_claim_amount)

            return True

    def delete_entry(self, server_id, user_id):
        server_date_hash = generate_objects_hash(server_id, include_date=True)
        user_id = str(user_id)
        records = UserClaimsByServer.objects(server_date_hash=server_date_hash, user_id=user_id).all()
        for record in records:
            self.money_repo.subtract_money(server_id, user_id, record.user_claim_amount)
            record.delete()

    def clear_all_entries(self):
        records = UserClaimsByServer.objects.all()
        for record in records:
            record.delete()
