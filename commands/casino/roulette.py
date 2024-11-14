import asyncio

from discord.ext import commands

from bot.database import DbConnector
from components.casino import (
    roulette,
    money,
)


class RouletteCommand:
    def __init__(self, ctx: commands.Context, connector: DbConnector):
        self.ctx = ctx
        self.connector = connector
        self.roulette_instance = roulette.Roulette()
        self.money_manager = money.MoneyService(self.connector)

    async def process(self, *args: str):
        if len(args) == 0:
            await self.ctx.reply('Nie podano argumentów\nMożliwe opcje: start, set, bet, help, prev, img')
            return
        if args[0] == 'start':
            if self.roulette_instance.is_game_started():
                await self.ctx.reply('Gra już się rozpoczęła')
                return
            await self.roulette_start()
        elif args[0] == 'set':
            if isinstance(int(args[1]), int):
                await self.set_round_time(int(args[1]))
        elif args[0] == 'bet':
            await self.roulette_betting(args[1:])
        elif args[0] == 'help':
            await self.ctx.reply('Możliwe opcje obstawiania:\n' + ', '.join(self.roulette_instance.get_possible_bets()))
        elif args[0] == 'prev':
            await self.show_previous_results()
        elif args[0] == 'img':
            await self.ctx.reply(
                'https://t3.ftcdn.net/jpg/04/09/51/40/360_F_409514024_hRZxuXUW7EhdjNMzZc7qJS30MLpD8yqg.jpg')

    async def show_previous_results(self, show_if_empty: bool = True):
        prev = self.roulette_instance.get_previous_results()
        if len(prev) == 0:
            if show_if_empty:
                await self.ctx.reply('Brak poprzednich wyników')
            return
        prev = [f'{p.number} :{p.get_color()}_circle:' for p in prev]
        await self.ctx.reply('Poprzednie wyniki: ' + ', '.join(prev))

    async def set_round_time(self, time: int):
        if self.roulette_instance.is_game_started():
            await self.ctx.reply('Gra już się rozpoczęła')
        elif 5 <= time <= 120:
            self.roulette_instance.set_round_time(time)
            await self.ctx.reply(f'Czas na zakłady ustawiony na {time} sekund')
        else:
            await self.ctx.reply('Podaj poprawny czas (od 5 do 120 sekund)')

    async def roulette_start(self):
        # starting game phase
        self.roulette_instance.start_game()
        await self.ctx.send('Rozpoczynanie gry')
        await self.show_previous_results(show_if_empty=False)
        await asyncio.sleep(self.roulette_instance.round_time)

        # betting phase
        self.roulette_instance.stop_game()
        await self.ctx.send('Koniec obstawiania!')
        self.roulette_instance.spin_wheel()
        await self.ctx.send('Losowanie')
        await asyncio.sleep(5)

        # drawing phase
        result: roulette.Field = self.roulette_instance.get_last_result()
        await self.ctx.send(f'Wylosowano {result} :{result.get_color()}_circle:')

        # checking bets phase
        winners = self.roulette_instance.get_winners()
        if len(winners) == 0:
            await self.ctx.send('Nikt nie wygrał')
            return
        # winner is dict with keys: id:nickname and values: amount
        for key, value in winners.items():
            user_id, nickname = key.split(':')
            await self.ctx.send(f'{nickname} wygrywa {value} cebulionów')
            self.money_manager.add_money(self.ctx.guild.id, user_id, value)

    async def roulette_betting(self, args):
        if not self.roulette_instance.is_game_started():
            await self.ctx.reply('Gra nie została rozpoczęta lub już trwa losowanie')
            return

        try:
            amount = int(args[0])
        except ValueError:
            await self.ctx.reply('Podaj poprawną kwotę')
            return
        bet_type = args[1:]
        bet_type = ' '.join(bet_type)
        bet = roulette.Bet(self.ctx.author.id, self.ctx.author.display_name, amount, bet_type)

        if amount <= 0:
            await self.ctx.reply('Podaj poprawną kwotę')
            return
        if len(bet_type) == 0:
            await self.ctx.reply(
                'Podaj typ zakładu\nMożliwe typy: ' + ', '.join(self.roulette_instance.get_possible_bets()))
            return
        if not self.roulette_instance.validate_bet(bet):
            await self.ctx.reply(
                'Niepoprawny typ zakładu\nMożliwe typy: ' + ', '.join(self.roulette_instance.get_possible_bets()))
            return
        user_money = self.money_manager.get_money(self.ctx.guild.id, self.ctx.author.id)
        if user_money < amount:
            await self.ctx.reply('Nie masz tyle pieniędzy')
            return
        if not self.roulette_instance.add_bet(bet):
            await self.ctx.reply('Możesz obstawić na max 10 pozycji')
            return
        self.money_manager.subtract_money(self.ctx.guild.id, self.ctx.author.id, amount)
        await self.ctx.reply(f'Obstawiasz {bet.amount} cebulionów na {bet.bet_type}')
