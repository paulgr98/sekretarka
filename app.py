import discord
from discord.ext import commands
import config as cfg
from asyncprawcore import exceptions
import logging
import datetime as dt
import time
import random
import math
import asyncio
from openai.error import OpenAIError

from components.uwuify import uwuify
from components.reddit import get_subreddit_random_hot
from components.demotes import get_demotes
from components.compliments import get_compliment_list
from components.disses import get_diss_list
from components.shipping import save_users_match_for_today, get_users_match_for_today, get_user_top_match

from components import (
    nameday as nd,
    tenor,
    epic_free_games as epic,
    essa,
    magic_ball,
    pp_len,
)
from components.casino import (
    roulette,
    money,
)

from commands import help
from commands import converter
from commands import free
from commands import alco_drink
from commands import weather
from commands import astrology
from commands import poll
from commands import generate_story

# bot instance
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)
client.remove_command('help')

# options for youtube_dl to download audio
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


# my user class
class Usr(object):
    def __init__(self):
        self.is_busy = False
        self.user = None
        self.nick = None


# owner configuration
owner = Usr()
owner.nick = 'PanPajonk'

bot_channels = ['bot', 'bot_nsfw', 'bot-spam', 'nsfw']

female_role = 'kobita'

# logger config
handler = logging.StreamHandler()
logger = logging.getLogger('discord')


# ----------------------------------------------------------------------------------------------------------------------

# handle errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Nie ma takiej komendy. Wpisz $pomoc żeby wyświetlić listę komend')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Brak argumentu. Wpisz $pomoc żeby wyświetlić listę komend')
    elif isinstance(error, commands.CommandOnCooldown):
        time_left = error.retry_after
        if time_left > 60:
            time_left = str(math.ceil(time_left / 60)) + ' min'
        else:
            time_left = str(int(time_left)) + ' sek'
        await ctx.send(f'Ta komenda posiada cooldown. Spróbuj znowu za {time_left}')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('Nie masz uprawnień do tej komendy')
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f'Niepoprawne argumenty. Jeśli używasz {client.command_prefix}rdt, '
                       f'upewnij się ze nazwa subreddit nie zawiera spacji')
    else:
        await ctx.send('Error! Insert kremówka! <a:jp2:985844814597742683>')
        logger.error(f'{error} ({error.__class__.__name__})')


# print message that the bot is ready
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user)
    print('-----------------')
    print('Ready to go!')


# on message convert content to lowercase
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$'):
        # lower only the first part of the message
        head = message.content.split(' ')[0]
        tail = message.content.split(' ')[1:]
        message.content = head.lower() + ' ' + ' '.join(tail)
        await client.process_commands(message)
    if owner.is_busy and f'<@{owner.user.id}>' in message.content:
        await message.channel.send('Prezes Pajonk obecnie jest zajęty. Spróbuj później')


# simple ping command
@client.command()
async def ping(ctx):
    await ctx.send('Jebnij się w łeb')


# simple hi command
@client.command()
async def hi(ctx):
    if ctx.author.name == owner.nick:
        await ctx.send('Hej skarbie ❤')
        return
    await ctx.send(f'Hej {ctx.author.name}')


# deleting given amount of messages above
@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount=2):
    if amount <= 50:
        await ctx.channel.purge(limit=amount)
    else:
        await ctx.send('Nie możesz usunąć więcej niż 50 jednocześnie')


# deleting given amount of messages send by the bot
@client.command()
async def undo(ctx, amount=1):
    await ctx.channel.purge(limit=1)
    # get last 200 messages
    # messages = await ctx.channel.history(limit=200).flatten() # flatten() removed
    messages = [msg async for msg in ctx.channel.history(limit=200)]
    # filter messages where the client is the bot
    messages = [m for m in messages if m.author == client.user]
    # limit the messages to the given amount
    messages = messages[:amount]
    # delete messages
    await ctx.channel.delete_messages(messages)


# compliment command that send one random compliment from predefined list
@client.command()
@commands.cooldown(1, 300, commands.BucketType.channel)
async def compliment(ctx, member=None):
    global bot_channels
    if ctx.channel.name in bot_channels:
        compliment.reset_cooldown(ctx)
    # check for female_role role in user's roles to check if the user is a female
    if member is None:
        is_female = female_role in [role.name for role in ctx.author.roles]
        # get compliment list
        compliments = get_compliment_list(ctx.author.name, is_female)
        await ctx.send(random.choice(compliments))
        return

    # try cast member to discord.Member
    try:
        member_converter = commands.MemberConverter()
        member = await member_converter.convert(ctx, member)
    except commands.BadArgument:
        pass

    if isinstance(member, discord.Member):
        is_female = female_role in [role.name for role in member.roles]
        name = member.name
        mention = member.mention
    else:
        is_female = False
        name = member
        mention = member
    compliments = get_compliment_list(name, is_female)
    await ctx.send(f'Komplement dla {mention}:\n{random.choice(compliments)}')


# diss command that send one random diss from predefined list
@client.command()
@commands.cooldown(1, 300, commands.BucketType.channel)
async def diss(ctx, member=None):
    global bot_channels
    if ctx.channel.name in bot_channels:
        diss.reset_cooldown(ctx)
    # check for female_role role in user's roles to check if the user is female
    if member is None:
        member = ctx.author

    # try cast member to discord.Member
    if not isinstance(member, discord.Member):
        try:
            member_converter = commands.MemberConverter()
            member = await member_converter.convert(ctx, member)
        except commands.BadArgument:
            pass

    # check if the member is instance of discord.Member
    if isinstance(member, discord.Member):
        is_female = female_role in [role.name for role in member.roles]
    else:
        is_female = False
    disses = get_diss_list(member, is_female)
    await ctx.send(random.choice(disses))


# the opposite of motivate command
@client.command()
async def demote(ctx):
    texts = get_demotes()
    await ctx.send(random.choice(texts))


# get random post from given subreddit
@client.command()
async def rdt(ctx, subreddit: str = 'memes', limit: int = 50):
    global bot_channels
    if ctx.channel.name not in bot_channels:
        await ctx.send(f'komendy {client.command_prefix}rdt można używać tylko na kanale do tego przeznaczonym')
        return
    try:
        post = await get_subreddit_random_hot(subreddit, ctx.author, limit)
    except commands.CommandError as e:
        await ctx.send(e)
        return
    except (exceptions.Forbidden, exceptions.NotFound):
        await ctx.send('Nie ma takiego subreddita, albo nie ma na nim obrazków :(')
        return

    title = post['title']
    # if title is too long, cut it
    if len(title) > 250:
        title = title[:250] + '...'
    embed = discord.Embed(title=title, color=0xFF5700)
    embed.set_author(name=post['author'])
    embed.set_image(url=post['url'])
    await ctx.send(embed=embed)


# uwuify the message above
@client.command()
async def uwu(ctx):
    # get message above command
    # message = await ctx.channel.history(limit=2).flatten() # flatten() removed
    message = [msg async for msg in ctx.channel.history(limit=2)]
    msg = message[1]
    uwus = ['UwU', 'OwO', '(*/ω＼*)', 'ヾ(≧▽≦*)o', '( •̀ ω •́ )✧', '（*＾-＾*）']
    await msg.reply(f"{uwuify(msg.content)} {random.choice(uwus)}")


# dictionary to store members to ban with the id of the message as key
to_ban = {}


# ban command. but not actually baning anyone. just for fun
@client.command()
async def ban(ctx, member: discord.Member):
    # if there are more than 5 people to ban, remove the oldest one
    if len(to_ban) > 5:
        del to_ban[min(to_ban, key=to_ban.get)]
    if member.name == owner.nick:
        await ctx.send('Nie masz tu mocy :sunglasses:')
        return
    if member.id == client.user.id:
        await ctx.send('Tylko buk może mnie sondzić!')
        return
    if member.id == ctx.author.id:
        message = await ctx.send(f'Tego chcesz? xD Spoko. 2 ❤ pod tą wiadomością i banujemy {ctx.author.mention}')
        to_ban[message.id] = member
        return
    message = await ctx.send(f'5 ❤ pod tą wiadomością i banujemy {member.mention}!')
    to_ban[message.id] = member


# if reaction is added to the ban message, count the heart reactions
@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return
    # get the message from reaction
    message = reaction.message

    # if the message is found in to_ban, ban the member
    if message.id in to_ban:
        member = to_ban[message.id]
        if '5 ❤ pod tą wiadomością i banujemy' in message.content and message.author.bot is True:
            if reaction.emoji == str("\u2764\ufe0f") and reaction.count == 5:
                await message.channel.send(f'No i banujemy {member.mention}!')
        elif '2 ❤ pod tą wiadomością i banujemy' in message.content and message.author.bot is True:
            if reaction.emoji == str("\u2764\ufe0f") and reaction.count == 2:
                await message.channel.send(f'No i banujemy {member.mention}! Na własne życzenie xD')


# TODO: research how to make this work and implement it (streamrip may work)
# cut random  fragment from given YouTube video
# @client.command()
# async def cut(ctx, url: str):
#     pass


@client.command('zw')
async def im_busy(ctx):
    if ctx.author.name == owner.nick:
        owner.is_busy = not owner.is_busy
        if owner.user is None:
            owner.user = ctx.author
        if owner.is_busy:
            await ctx.send('Prezes Pajonk wychodzi na ważne spotkanie')
        else:
            await ctx.send('Prezes Pajonk właśnie wrócił!')


# command to find gf or bf for the user
@client.command()
async def shipme(ctx):
    # get list of all users in the server
    users = ctx.guild.members
    # try to get user from already existing list for today
    ship_id = get_users_match_for_today(str(ctx.guild.id), str(ctx.author.id))
    if ship_id is not None:
        ship = client.get_user(int(ship_id))
        await ctx.send(f'{ctx.author.mention} myślę, że najlepszy ship na dzisiaj dla Ciebie to... {ship.mention}!')
        return

    # get list of users with role female_role
    females = []
    for u in users:
        roles = [r.name for r in u.roles]
        if female_role in roles and 'bot' not in roles:
            females.append(u)

    males = []
    for u in users:
        roles = [r.name for r in u.roles]
        if u not in females and 'bot' not in roles:
            males.append(u)

    # if messege author is in females, ship with males
    if ctx.author in females:
        ship = random.choice(males)
    else:
        ship = random.choice(females)

    # save ship to file
    save_users_match_for_today(ctx.guild.id, ctx.author.id, ship.id)
    await ctx.send(f'{ctx.author.mention} myślę, że najlepszy ship na dzisiaj dla Ciebie to... {ship.mention}!')


# command to see your top ship from all time
@client.command()
async def shipstat(ctx):
    # get list of all users in the server
    users = ctx.guild.members
    # get top ship for the user
    top_ship_id = get_user_top_match(str(ctx.author.id))
    if top_ship_id is None:
        await ctx.send(f'{ctx.author.mention} nie ma jeszcze żadnego shipa!')
        return
    if top_ship_id in [u.id for u in users]:
        top_ship = client.get_user(int(top_ship_id))
        await ctx.send(f'{ctx.author.mention} Twój najlepszy ship od początku to... {top_ship.mention}!')
        return
    await ctx.send(f'{ctx.author.mention} Twojego najlepszego shipa (ID: {top_ship_id}) nie ma w serwerze :/')


# command to get daily horoscopes for the user
@client.command()
async def astro(ctx, sign: str):
    global bot_channels
    if ctx.channel.name not in bot_channels:
        await ctx.send(f'komendy {client.command_prefix}astro można używać tylko na kanale do tego przeznaczonym')
        return

    try:
        embed = astrology.make_astrology_embed(sign)
        await ctx.send(embed=embed)
    except astrology.NoSignException as e:
        await ctx.send(e)
        return


# command to check for name days
@client.command()
async def nameday(ctx):
    names = nd.get_names()
    today = dt.datetime.now().strftime('%d.%m.%Y')
    # merge names from list to string with spaces and comma between names
    name_string = ', '.join(names)
    embed = discord.Embed(title=f'Imieniny na dzień {today}', color=0x4CC2F5)
    embed.add_field(name='Imieniny obchodzą: ', value=name_string, inline=False)
    await ctx.send(embed=embed)


# command to get weather forecast for the given city
@client.command()
async def wthr(ctx, city: str = 'Warszawa', days: int = 0):
    global bot_channels
    if ctx.channel.name not in bot_channels:
        await ctx.send(f'komendy {client.command_prefix}wthr można używać tylko na kanale do tego przeznaczonym')
        return

    if days > 4:
        await ctx.send('Pogodę można sprawdzić maksymalnie na 4 dni')
        return

    try:
        embed = weather.make_weather_embed(city, days)
        await ctx.send(embed=embed)
    except weather.WeatherException as e:
        await ctx.send(e)


# command to get random number between given range
@client.command()
async def roll(ctx, minimum: int = 1, maximum: int = 6):
    if minimum < 0 or maximum < 0:
        await ctx.send('Wartości muszą być większe lub równe 0')
        return
    if maximum > 999999:
        await ctx.send('Maksymalna wartość to 999999')
        return
    if minimum > maximum:
        await ctx.send(f'Wylosowano... {random.randint(maximum, minimum)}!')
    await ctx.send(f'Wylosowano... {random.randint(minimum, maximum)}!')


# command to throw a coin
@client.command()
async def coin(ctx):
    coin_flip = random.randint(0, 1)
    if coin_flip == 0:
        await ctx.send('Wypadł orzeł!')
        return
    await ctx.send('Wypadła reszka!')


# dictionary to save user id and their start time
stopwatch_dict = {}


# simple stopwatch command to measure time
@client.command(aliases=['sw'])
async def stopwatch(ctx, action: str):
    if action == 'start':
        if ctx.author.id in stopwatch_dict:
            await ctx.message.reply('Twór timer już wystartował')
            return
        stopwatch_dict[ctx.author.id] = time.time()
        await ctx.message.reply('Timer wystartował')
    elif action == 'stop':
        if ctx.author.id not in stopwatch_dict:
            await ctx.message.reply('Nie wystartowałeś jeszcze timera')
            return
        time_elapsed = time.time() - stopwatch_dict[ctx.author.id]
        # if the time is more than a minute, display it in minutes and seconds
        if time_elapsed > 60:
            await ctx.message.reply(f'Czas: {time_elapsed // 60:.0f} min. {time_elapsed % 60:.2f} sek.')
        # if the time is less than a minute, display it in seconds
        else:
            await ctx.message.reply(f'Czas: {time_elapsed:.2f} sek.')
        # delete the user's id from the dictionary
        stopwatch_dict.pop(ctx.author.id)
    elif action == 'reset':
        if ctx.author.id not in stopwatch_dict:
            await ctx.message.reply('Nie wystartowałeś jeszcze timera')
            return
        stopwatch_dict[ctx.author.id] = time.time()
        await ctx.message.reply('Zresetowano timer')
    else:
        await ctx.message.reply('Wpisz start, stop lub reset')


@client.command('poll')
async def create_poll(ctx, *, content: str):
    # remove whitespaces from the beginning and end of the string
    content = content.strip()
    # if the string is empty, return
    if not content:
        await ctx.send('Nie wpisałeś treści')
        return
    # if the string is too long, return
    if len(content) > 250:
        await ctx.send('Za długa treść')
        return

    # replace whitespaces before and after ; sign
    content = content.replace('; ', ';')
    content = content.replace(' ;', ';')

    # seprate the content into question and options (separated by ';')
    content_list = content.split(';')
    question = poll.init_cap(content_list[0])
    options = content_list[1:]

    if 2 > len(options) > 10:
        await ctx.send('Możliwa ilość odpowiedzi to od 2 do 10')
        return

    embed, reactions = poll.create_embed(question, options)

    msg = await ctx.send(embed=embed)
    # add reactions to the message
    for reaction in reactions:
        await msg.add_reaction(reaction)


@client.command('essa')
async def calc_essa(ctx, *, member=None):
    if member is None:
        member = ctx.author

    # if member is instance of discord.Member
    if isinstance(member, discord.Member):
        nickname = member.name
    else:
        nickname = member

    essa_level = essa.calculate_essa_level(nickname)
    await ctx.send(f'{nickname} ma {essa_level}% essy')


# command to get a random cocktail recipe or search for a specific one form thecocktaildb.com
@client.command()
async def drink(ctx: commands.Context, *drink_name: str):
    name = ' '.join(drink_name)
    embed = alco_drink.make_drink_embed(name)
    if embed is None:
        await ctx.send('Nie znaleziono drinka :/')
        return
    await ctx.send(embed=embed)


# free epic store games
@client.command('free')
async def epic_free_games(ctx: commands.Context, period: str = 'current'):
    try:
        free_games = epic.get_free_games(period)
    except ValueError:
        await ctx.send('Niepoprawny okres. Możliwe wartości: current, upcoming')
        return
    for game in free_games:
        embed = free.make_game_embed(game, period)
        await ctx.send(embed=embed)


async def send_gif(ctx: commands.Context, *search_query: str, is_random: bool = True):
    query = ' '.join(search_query)
    ten = tenor.Tenor()
    gif = ten.get_gif(query, random=is_random)
    if gif is None or gif == '':
        await ctx.send(f'{ctx.author.mention}, nie znaleziono GIFa :/')
        return
    await ctx.send(f'{ctx.author.mention} {gif}')


@client.command('gif')
async def send_random_gif(ctx: commands.Context, *search_query: str):
    await send_gif(ctx, *search_query, is_random=True)


@client.command('topgif')
async def send_top_gif(ctx: commands.Context, *search_query: str):
    await send_gif(ctx, *search_query, is_random=False)


@client.command('convert')
async def convert(ctx: commands.Context, method: str, *args: str):
    text = ' '.join(args)
    result = converter.convert(method, text)
    await ctx.reply(result)


@client.command('8ball')
async def eight_ball(ctx: commands.Context):
    answer = magic_ball.get_random_answer()
    await ctx.reply(answer)


@client.command('pp')
async def pp_length(ctx: commands.Context, member=None):
    if member is None:
        member = ctx.author

    if isinstance(member, str):
        pp = pp_len.get_pp_len(member)
        await ctx.reply(f'{member} ma {pp} cm siurka :3')
    else:
        pp = pp_len.get_pp_len(member.name)
        await ctx.reply(f'{member.mention} ma {pp} cm siurka :3')


@client.command('story')
async def story(ctx: commands.Context, *keywords: str):
    # check if there are any keywords
    if len(keywords) == 0:
        await ctx.reply('Podaj słowo kluczowe (np. kot)')
        return
    prompt = ' '.join(keywords)
    # check for api errors
    try:
        # trigger typing
        async with ctx.typing():
            story_pl = generate_story.generate_story(prompt)
        await ctx.reply(story_pl)
    except OpenAIError as e:
        if e.http_status == 402:
            await ctx.reply('Przekroczono limit zapytań')


roulette_instance = roulette.Roulette()


@client.command('roulette')
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
        return
    if args[0] == 'set':
        if isinstance(int(args[1]), int):
            if roulette_instance.is_game_started():
                await ctx.reply('Gra już się rozpoczęła')
                return
            elif 5 <= int(args[1]) <= 120:
                roulette_instance.set_round_time(int(args[1]))
                await ctx.reply(f'Czas na zakłady ustawiony na {args[1]} sekund')
                return
            else:
                await ctx.reply('Podaj poprawny czas (od 5 do 120 sekund)')
                return
    if args[0] == 'bet':
        await roulette_betting(ctx, args[1:])


async def roulette_start(ctx: commands.Context):
    global roulette_instance
    roulette_instance.start_game()
    await ctx.send('Rozpoczynanie gry')
    await asyncio.sleep(roulette_instance.round_time)
    roulette_instance.stop_game()
    await ctx.send('Koniec obstawiania!')
    roulette_instance.spin_wheel()
    await ctx.send('Losowanie')
    await asyncio.sleep(5)
    result = roulette_instance.get_last_result()
    await ctx.send(f'Wylosowano {result}')
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


@client.command('money')
async def money_command(ctx: commands.Context, *args: str):
    money_manager = money.MoneyManager(ctx.author.id)
    if len(args) == 0:
        await ctx.reply('Nie podano argumentów. \nDostępne argumenty: check, claim, add, ranking')
        return
    if args[0] == 'check':
        await ctx.reply(f'Masz {money_manager.get_money()} cebulionów')
        return
    if args[0] == 'claim':
        if money_manager.claim_daily():
            await ctx.reply(f'Otrzymałeś {money_manager.daily_amount} cebulionów')
            return
        else:
            await ctx.reply('Już otrzymałeś dziś darmowe pieniądze cebulaku!')
            return
    if args[0] == 'add':
        # get list of user roles
        roles = [role.name for role in ctx.author.roles]
        if 'admin' in roles:
            if len(args) < 2:
                await ctx.reply('Nie podano kwoty')
                return
            if isinstance(int(args[1]), int):
                money_manager.add_money(int(args[1]))
                await ctx.reply(f'Dodano {args[1]} cebulionów')
                return
            else:
                await ctx.reply('Podaj poprawną kwotę')
                return
        else:
            await ctx.reply('Nie masz uprawnień do tej komendy')
            return
    if args[0] == 'ranking':
        ranking = money_manager.get_ranking()
        for user_id, amount in ranking:
            # find user by id
            user = await client.fetch_user(user_id)
            await ctx.send(f'{user.name} - {amount} cebulionów')
        return
    else:
        await ctx.reply('Niepoprawny argument.\nMożliwe argumenty: check, claim, add, ranking')


# help command to show all commands
@client.command('pomoc')
async def help_command(ctx: commands.Context):
    embeds = help.get_help_embed(client.command_prefix)
    for embed in embeds:
        await ctx.send(embed=embed)

# run the bot
client.run(cfg.TOKEN)
