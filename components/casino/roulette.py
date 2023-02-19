import random


class Bet(object):
    def __init__(self, user_id, user_nickname, amount, bet_type):
        self.user_nickname = user_nickname
        self.user_id = user_id
        self.amount = amount
        self.bet_type = bet_type
        self.win_amount = 0

    def get_multiplier(self):
        if self.bet_type == 'even' or self.bet_type == 'odd':
            return 2
        elif self.bet_type == 'red' or self.bet_type == 'black':
            return 2
        elif self.bet_type == '1-18' or self.bet_type == '19-36':
            return 2
        elif self.bet_type == '1st 12' or self.bet_type == '2nd 12' or self.bet_type == '3rd 12':
            return 3
        elif self.bet_type == '1st row' or self.bet_type == '2nd row' or self.bet_type == '3rd row':
            return 3
        else:
            return 36


class Roulette(object):
    def __init__(self):
        self.round_time = 60
        self.wheel = Wheel()
        self.bets = []
        self.last_result: Field = Field(0)
        self.is_started = False
        self.possible_bets = ['Liczby od 0 do 36',
                              'even', 'odd',
                              'red', 'black',
                              '1-18', '19-36',
                              '1st 12', '2nd 12', '3rd 12',
                              '1st row', '2nd row', '3rd row']
        for i in range(0, 37):
            field = Field(i)
            self.wheel.add_field(field)

    def set_round_time(self, time):
        self.round_time = time

    def is_game_started(self):
        return self.is_started

    def get_possible_bets(self):
        return self.possible_bets

    def validate_bet(self, bet: Bet):
        if bet.bet_type in self.get_possible_bets():
            return True
        elif str(bet.bet_type).isdigit() and 0 <= int(bet.bet_type) <= 36:
            return True
        else:
            return False

    def start_game(self):
        self.clear_bets()
        self.is_started = True

    def get_previous_results(self):
        prev = self.wheel.get_last_outcomes(5)
        prev = [p.number for p in prev]
        return prev

    def stop_game(self):
        self.is_started = False

    def add_bet(self, bet: Bet):
        # check if user id is already in bets
        user_bets = 0
        for b in self.bets:
            if b.user_id == bet.user_id:
                user_bets += 1
        if user_bets >= 10:
            return False
        self.bets.append(bet)
        return True

    def spin_wheel(self):
        self.last_result = self.wheel.spin()
        return self.last_result

    def get_last_result(self):
        return self.last_result

    def get_winners(self) -> dict[str, int]:
        winner_bets = []
        for bet in self.bets:
            if (bet.bet_type == self.last_result.get_row()) or \
                    (bet.bet_type == self.last_result.get_twelve()) or \
                    (bet.bet_type == self.last_result.get_half()) or \
                    (bet.bet_type == self.last_result.get_color()) or \
                    (bet.bet_type == self.last_result.get_odd_even()) or \
                    (str(bet.bet_type) == str(self.last_result.number)):
                bet.win_amount = bet.amount * bet.get_multiplier()
                winner_bets.append(bet)

        winners = {}
        for bet in winner_bets:
            if f'{bet.user_id}:{bet.user_nickname}' in winners:
                winners[f'{bet.user_id}:{bet.user_nickname}'] += bet.win_amount
            else:
                winners[f'{bet.user_id}:{bet.user_nickname}'] = bet.win_amount

        return winners

    def clear_bets(self):
        self.bets = []


class Wheel(object):
    def __init__(self):
        self.outcomes = []
        self.rng = random.Random()
        self.fields = []

    def spin(self):
        result = self.rng.choice(self.fields)
        self.outcomes.append(result)
        return result

    def get_last_outcomes(self, number):
        prev = self.outcomes[-number:]
        prev.reverse()
        return prev

    def add_field(self, field):
        self.fields.append(field)


class Field(object):
    def __init__(self, number):
        self.number = number

    def get_color(self):
        if self.number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
            return "red"
        elif self.number in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]:
            return "black"
        else:
            return "green"

    def get_row(self):
        if self.number in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]:
            return '1st row'
        elif self.number in [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]:
            return '2nd row'
        elif self.number in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]:
            return '3rd row'
        else:
            return '0'

    def get_twelve(self):
        if self.number in range(1, 13):
            return '1st 12'
        elif self.number in range(13, 25):
            return '2nd 12'
        elif self.number in range(25, 37):
            return '3rd 12'
        else:
            return '0'

    def get_half(self):
        if self.number in range(1, 19):
            return '1-18'
        elif self.number in range(19, 37):
            return '19-36'
        else:
            return '0'

    def get_odd_even(self):
        if self.number % 2 == 0:
            return 'even'
        else:
            return 'odd'

    def __str__(self):
        return str(self.number)

    def __repr__(self):
        return str(self.number)
