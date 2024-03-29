import asyncio

from discord.ext import commands

from components.casino import (
    roulette,
    money,
)

roulette_instance = roulette.Roulette()


async def roulette_main(ctx: commands.Context, *args: str):
    global roulette_instance
    if len(args) == 0:
        await ctx.reply('Nie podano argumentów')
        return
    if args[0] == 'start':
        if roulette_instance.is_game_started():
            await ctx.reply('Gra już się rozpoczęła')
            return
        await roulette_start(ctx)
    elif args[0] == 'set':
        if isinstance(int(args[1]), int):
            await set_round_time(ctx, int(args[1]))
    elif args[0] == 'bet':
        await roulette_betting(ctx, args[1:])
    elif args[0] == 'help':
        await ctx.reply('Możliwe opcje obstawiania:\n' + ', '.join(roulette_instance.get_possible_bets()))
    elif args[0] == 'prev':
        await show_previous_results(ctx)
    elif args[0] == 'img':
        await ctx.reply('https://t3.ftcdn.net/jpg/04/09/51/40/360_F_409514024_hRZxuXUW7EhdjNMzZc7qJS30MLpD8yqg.jpg')


async def show_previous_results(ctx: commands.Context, show_if_empty: bool = True):
    prev = roulette_instance.get_previous_results()
    if len(prev) == 0:
        if show_if_empty:
            await ctx.reply('Brak poprzednich wyników')
        return
    prev = [f'{p.number} :{p.get_color()}_circle:' for p in prev]
    await ctx.reply('Poprzednie wyniki: ' + ', '.join(prev))


async def set_round_time(ctx, time: int):
    global roulette_instance
    if roulette_instance.is_game_started():
        await ctx.reply('Gra już się rozpoczęła')
    elif 5 <= time <= 120:
        roulette_instance.set_round_time(time)
        await ctx.reply(f'Czas na zakłady ustawiony na {time} sekund')
    else:
        await ctx.reply('Podaj poprawny czas (od 5 do 120 sekund)')


async def roulette_start(ctx: commands.Context):
    # starting game phase
    global roulette_instance
    roulette_instance.start_game()
    await ctx.send('Rozpoczynanie gry')
    await show_previous_results(ctx, show_if_empty=False)
    await asyncio.sleep(roulette_instance.round_time)

    # betting phase
    roulette_instance.stop_game()
    await ctx.send('Koniec obstawiania!')
    roulette_instance.spin_wheel()
    await ctx.send('Losowanie')
    await asyncio.sleep(5)

    # drawing phase
    result: roulette.Field = roulette_instance.get_last_result()
    await ctx.send(f'Wylosowano {result} :{result.get_color()}_circle:')

    # checking bets phase
    winners = roulette_instance.get_winners()
    if len(winners) == 0:
        await ctx.send('Nikt nie wygrał')
        return
    # winner is dict with keys: id:nickname and value: amount
    for key, value in winners.items():
        user_id, nickname = key.split(':')
        await ctx.send(f'{nickname} wygrywa {value} cebulionów')
        money_manager = money.MoneyManager(user_id)
        money_manager.add_money(value)


async def roulette_betting(ctx: commands.Context, args):
    global roulette_instance
    if not roulette_instance.is_game_started():
        await ctx.reply('Gra nie została rozpoczęta lub już trwa losowanie')
        return

    amount = 0
    if isinstance(int(args[0]), int):
        amount = int(args[0])
    bet_type = args[1:]
    bet_type = ' '.join(bet_type)
    bet = roulette.Bet(ctx.author.id, ctx.author.name, amount, bet_type)

    if amount <= 0:
        await ctx.reply('Podaj poprawną kwotę')
        return
    if len(bet_type) == 0:
        await ctx.reply('Podaj typ zakładu\nMożliwe typy: ' + ', '.join(roulette_instance.get_possible_bets()))
        return
    if not roulette_instance.validate_bet(bet):
        await ctx.reply('Niepoprawny typ zakładu\nMożliwe typy: ' + ', '.join(roulette_instance.get_possible_bets()))
        return
    money_manager = money.MoneyManager(ctx.author.id)
    if money_manager.get_money() < amount:
        await ctx.reply('Nie masz tyle pieniędzy')
        return
    if not roulette_instance.add_bet(bet):
        await ctx.reply('Możesz obstawić na max 10 pozycji')
        return
    money_manager.remove_money(amount)
    await ctx.reply(f'Obstawiasz {bet.amount} cebulionów na {bet.bet_type}')
