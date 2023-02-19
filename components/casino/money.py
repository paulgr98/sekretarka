import os
import json
import datetime


class MoneyManager(object):
    def __init__(self, user_id):
        self.money_path = 'data/casino/money.json'
        self.claims_path = 'data/casino/claims.json'
        self.user_id = str(user_id)
        self.money = {}
        self.claims = {}
        self.daily_amount = 1000
        self.load_money()
        self.load_daily_claims()

    def load_money(self):
        if os.path.exists(self.money_path):
            # if file exists, but has no json data
            if os.stat(self.money_path).st_size == 0:
                self.save_money()
            with open(self.money_path, 'r') as f:
                self.money = json.load(f)
        else:
            # create path if it doesn't exist
            os.makedirs(os.path.dirname(self.money_path), exist_ok=True)
            self.save_money()

    def save_money(self):
        with open(self.money_path, 'w') as f:
            json.dump(self.money, f, indent=4)

    def get_money(self):
        if self.user_id in self.money:
            return self.money[self.user_id]
        else:
            return 0

    def add_money(self, amount):
        if self.user_id in self.money:
            self.money[self.user_id] += amount
        else:
            self.money[self.user_id] = amount
        self.save_money()

    def remove_money(self, amount):
        if self.user_id in self.money:
            self.money[self.user_id] -= amount
        else:
            self.money[self.user_id] = 0
        self.save_money()

    def load_daily_claims(self):
        if os.path.exists(self.claims_path):
            # if file exists, but has no json data
            if os.stat(self.claims_path).st_size == 0:
                self.save_daily_claims()
            with open(self.claims_path, 'r') as f:
                self.claims = json.load(f)
        else:
            # create path if it doesn't exist
            os.makedirs(os.path.dirname(self.claims_path), exist_ok=True)
            self.save_daily_claims()

    def save_daily_claims(self):
        with open(self.claims_path, 'w') as f:
            json.dump(self.claims, f, indent=4)

    def claim_daily(self):
        claim_id = f'{self.user_id}:{datetime.datetime.now().strftime("%Y-%m-%d")}'
        if claim_id in self.claims:
            return False
        else:
            self.claims[claim_id] = True
            self.save_daily_claims()
            self.add_money(self.daily_amount)
            return True

    def get_ranking(self):
        ranking = []
        for user_id, money in self.money.items():
            ranking.append((user_id, money))
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking
