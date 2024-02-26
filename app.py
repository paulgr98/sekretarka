import config as cfg
import asyncio
import datetime as dt
import logging
import math
import random
import time
from threading import Thread

import discord
from discord.ext import commands
from openai import APIError, RateLimitError, APIConnectionError

from commands import alco_drink
from commands import astrology
from commands import birthday_tracker as bt
from commands import calendar
from commands import converter
from commands import f1cmd
from commands import free
from commands import generate_story
from commands import help
from commands import poll
from commands import weather
from commands import smart_light as sl
from commands import text_to_speach as tts
from commands.casino import money as money_cmd
from commands.casino import roulette as roulette_cmd
from components import (
    nameday as nd,
    tenor,
    epic_free_games as epic,
    essa,
    magic_ball,
    pp_len,
    morning_routine as mr,
    f1 as f1schedule,
    random_yt,
    utility as util
)
from components.compliments import get_compliment_list
from components.demotes import get_demotes
from components.disses import get_diss_list
from components.openai_models import ChatGPT4Free, run_api
from components.reddit import get_subreddit_random_hot, SubredditOver18
from components.shipping import save_users_match_for_today, get_users_match_for_today, get_user_top_match
from components.uwuify import uwuify
from components.gpt_chat_history import ChatHistory, Message, GptRole

# bot instance
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='b$', intents=intents)
client.remove_command('help')


# my user class
class Usr(object):
    def __init__(self):
        self.is_busy = False
        self.user = None
        self.nick = None


# owner configuration
owner = Usr()
owner.nick = 'panpajonk'

my_gf = Usr()
my_gf.nick = 'marta.6442'

bot_channels = ['bot', 'bot_nsfw', 'bot-spam', 'nsfw', 'machine-learning']
nsfw_channels = ['bot_nsfw', 'nsfw']

female_role = 'kobita'

# logger config
handler = logging.StreamHandler()
logger = logging.getLogger('discord')

users_chat_history = ChatHistory()

error_messages = {
    'no_permission': 'Nie masz uprawnień do tej komendy',
}

DISCORD_MESSAGE_LEN_LIMIT = 2000


# ----------------------------------------------------------------------------------------------------------------------

# handle errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Nie ma takiej komendy. Wpisz {client.command_prefix}pomoc żeby wyświetlić listę komend')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Brak argumentu. Wpisz {client.command_prefix}pomoc żeby wyświetlić listę komend')
    elif isinstance(error, commands.CommandOnCooldown):
        time_left = error.retry_after
        if time_left > 60:
            time_left = str(math.ceil(time_left / 60)) + ' min'
        else:
            time_left = str(int(time_left)) + ' sek'
        await ctx.send(f'Ta komenda posiada cooldown. Spróbuj znowu za {time_left}')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(error_messages['no_permission'])
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
    await asyncio.create_task(mr.schedule_morning_routine(client, show_news=False))
    # asyncio.create_task(f1schedule.schedule_f1_notifications(client))


# on message convert content to lowercase
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith(client.command_prefix):
        # lower only the first part of the message
        head = message.content.split(' ')[0]
        tail = message.content.split(' ')[1:]
        message.content = head.lower() + ' ' + ' '.join(tail)
        await client.process_commands(message)
    if owner.is_busy and f'<@{owner.user.id}>' in message.content:
        await message.channel.send('Prezes Pajonk obecnie jest zajęty. Spróbuj później')
    if my_gf.is_busy and f'<@{my_gf.user.id}>' in message.content:
        await message.channel.send('Pani Prezes obecnie jest zajęta. Spróbuj później')


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


# get user's avatar in embed
@client.command()
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed_title = f'{member.display_name}'
    if member.name != member.display_name:
        embed_title += f' ({member.name})'
    embed = discord.Embed(title=embed_title, color=0x328CED)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


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
@commands.cooldown(1, 60, commands.BucketType.channel)
async def compliment(ctx, member=None):
    global bot_channels
    if ctx.channel.name in bot_channels:
        compliment.reset_cooldown(ctx)
    # check for female_role role in user's roles to check if the user is a female
    if member is None:
        is_female = util.has_role(female_role, ctx.author)
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
        is_female = util.has_role(female_role, member)
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
@commands.cooldown(1, 60, commands.BucketType.channel)
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
        is_female = util.has_role(female_role, member)
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
    global bot_channels, nsfw_channels
    post = None
    if ctx.channel.name not in bot_channels:
        await ctx.send(f'komendy {client.command_prefix}rdt można używać tylko na kanale do tego przeznaczonym')
        return
    try:
        is_channel_nsfw: bool = str(ctx.channel.name).lower() in nsfw_channels
        post = await get_subreddit_random_hot(subreddit, is_channel_nsfw, limit)
    except SubredditOver18 as e:
        # if channel is not nsfw, send message
        if str(ctx.channel.name).lower() not in nsfw_channels:
            await ctx.send(e)
            return
    except commands.CommandError as e:
        await ctx.send(e)
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
    elif ctx.author.name == my_gf.nick:
        my_gf.is_busy = not my_gf.is_busy
        if my_gf.user is None:
            my_gf.user = ctx.author
        if my_gf.is_busy:
            await ctx.send('Pani Prezes wychodzi na ważne spotkanie')
        else:
            await ctx.send('Pani Prezes właśnie wróciła!')


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

    # if message author is in females, ship with males
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

    # separate the content into question and options (separated by ';')
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
    global bot_channels
    if ctx.channel.name not in bot_channels:
        await ctx.reply(f'Komendy {client.command_prefix}free można używać tylko na kanale do tego przeznaczonym')
        return
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


# command to generate a story using OpenAI API
@client.command('story')
async def story(ctx: commands.Context, *keywords: str):
    global bot_channels
    if ctx.channel.name not in bot_channels:
        await ctx.reply(f'Komendy {client.command_prefix}story można używać tylko na kanale do tego przeznaczonym')
        return
    # check if there are any keywords
    if len(keywords) == 0:
        await ctx.reply('Podaj słowo kluczowe (np. kot)')
        return
    prompt = ' '.join(keywords)
    # check for api errors
    try:
        # trigger typing
        async with ctx.typing():
            story_task = asyncio.create_task(generate_story.generate_story(prompt))
            story_txt = await story_task
        # if response is longer than Discord limit, send it in chunks
        if len(story_txt) > DISCORD_MESSAGE_LEN_LIMIT:
            story_chunks = util.split_into_chunks(story_txt, DISCORD_MESSAGE_LEN_LIMIT)
            for chunk in story_chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(story_txt)
    except APIConnectionError:
        await ctx.reply('Nie udało się połączyć z API')
    except APIError as e:
        if e.code == 402:
            await ctx.reply('Przekroczono limit zapytań')
        elif e.code == 429:
            testo_bytes = tenor.url_to_file('https://media.tenor.com/A4Tnhi1KDOAAAAAC/testoviron.gif')
            # load bytes to file
            testo_file = discord.File(testo_bytes, filename='testoviron.gif')
            await ctx.reply('Przekroczono limit zapytań...'
                            '\n\nAaaa kuhwa, nie dla psa kuhwa, nie dla śmiecia, dla pana to',
                            file=testo_file)
            return
        elif e.code is not None:
            await ctx.reply(f'Nieznany błąd z kodem {e.code}')
        else:
            await ctx.reply('Nieznany błąd')


@client.command(aliases=['rr', 'roulette'])
async def roulette_command(ctx: commands.Context, *args: str):
    global bot_channels
    if ctx.channel.name not in bot_channels:
        await ctx.reply('Tej komendy można używać tylko na kanale do tego przeznaczonym')
        return
    await roulette_cmd.roulette_main(ctx, *args)


@client.command('money')
async def money_command(ctx: commands.Context, *args: str):
    await money_cmd.money_command(ctx, client, *args)


@client.command('morning')
async def test_morning_routine(ctx: commands.Context):
    await mr.morning_routine(client, show_news=True)


@client.command('bday')
async def birthday_command(ctx: commands.Context, action: str, *args: str):
    await bt.birthday_main(ctx, action, *args)


@client.command('gpt')
async def gpt_command(ctx: commands.Context, *args: str):
    gpt = ChatGPT4Free()
    msg = handle_gpt_args(ctx, *args)
    if msg is not None:
        await ctx.reply(msg)
        return

    prompt = ' '.join(args)
    try:
        async with ctx.typing():
            # get users chat history
            previous_messages = users_chat_history.get(ctx.author.id)
            if previous_messages is None:
                response_task = asyncio.create_task(gpt.complete(prompt))
            else:
                response_task = asyncio.create_task(gpt.complete(prompt, previous_messages))
            response = await response_task
    except RateLimitError:
        testo_bytes = tenor.url_to_file('https://media.tenor.com/A4Tnhi1KDOAAAAAC/testoviron.gif')
        # load bytes to file
        testo_file = discord.File(testo_bytes, filename='testoviron.gif')
        await ctx.reply('Przekroczono limit zapytań...'
                        '\n\nAaaa kuhwa, nie dla psa kuhwa, nie dla śmiecia, dla pana to',
                        file=testo_file)
        return
    except APIConnectionError:
        await ctx.reply('Nie udało się połączyć z API')
        return
    # if response is longer than Discord limit, send it in chunks
    if len(response) > DISCORD_MESSAGE_LEN_LIMIT:
        response_chunks = util.split_into_chunks(response, DISCORD_MESSAGE_LEN_LIMIT)
        for chunk in response_chunks:
            await ctx.send(chunk)
    else:
        # if there are no errors, add both messages to history
        users_chat_history.add(ctx.author.id, Message(prompt, GptRole.USER))
        users_chat_history.add(ctx.author.id, Message(response, GptRole.ASSISTANT))
        await ctx.send(response)


def handle_gpt_args(ctx: commands.Context, *args: str, ):
    global users_chat_history
    if len(args) == 0:
        return 'Nie podano argumentów'
    if args[0] == '--clear':
        users_chat_history.clear(ctx.author.id)
        return 'Historia została wyczyszczona'
    return None


@client.command('f1')
async def f1_command(ctx: commands.Context):
    embed = f1cmd.make_next_race_embed()
    await ctx.send("Następny wyścig", embed=embed)


# help command to show all commands
@client.command(aliases=['pomoc', 'help'])
async def help_command(ctx: commands.Context):
    global bot_channels
    if ctx.channel.name not in bot_channels:
        await ctx.reply('Tej komendy można używać tylko na kanale do tego przeznaczonym')
        return
    embeds = help.get_help_embed(client.command_prefix)
    for embed in embeds:
        await ctx.send(embed=embed)


@client.command('calendar')
async def calendar_command(ctx: commands.Context, *args: str):
    if ctx.author.name != owner.nick:
        await ctx.send(error_messages['no_permission'])
        return
    events = calendar.get_next_event()
    if events is None:
        await ctx.send('Nie znaleziono żadnych wydarzeń')
        return
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # make date from 2023-10-06T10:30:00+02:00 to 06.10.2023 10:30
        start = dt.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y %H:%M')
        await ctx.send(f'{event["summary"]} - {start}')


@client.command('ryt')
async def ryt_command(ctx: commands.Context, *args: str):
    rand_id = random_yt.youtube_search()
    await ctx.send(f'https://www.youtube.com/watch?v={rand_id}')


@client.command('lights')
async def lights_command(ctx: commands.Context, *args: str):
    if not util.has_role('HR', ctx.author):
        await ctx.send(error_messages['no_permission'])
        return
    if args[0] == 'main':
        sl.switch_main_lights()
        await ctx.send('Przełączono światła główne')
    if args[0] == 'additional':
        sl.switch_additional_lights()
        await ctx.send('Przełączono światła dodatkowe')
    if args[0] == 'status':
        status = sl.get_status()
        await ctx.send(status)
    if args[0] == 'wakeup':
        owner_member = await util.get_user_from_username(ctx, owner.nick)
        await ctx.send(f'Budzimy {owner_member.mention}!')
        sl.wake_up()


@client.command('tts')
async def text_to_speach_command(ctx: commands.Context, *args: str):
    tts_client = tts.TextToSpeach(client)
    if len(args) == 0:
        await ctx.send('Brak argumentów')
        return
    if args[0] == '--join':
        await tts_client.join_voice_channel(ctx)
        return
    if args[0] == '--leave':
        await tts_client.leave_voice_channel(ctx)
        return
    await tts_client.text_to_speach(ctx, ' '.join(args))


def main():
    # run api on other thread
    api_thread = Thread(target=asyncio.run, args=(run_api(),))
    api_thread.start()
    # run main
    client.run(cfg.TOKEN_BETA)


if __name__ == '__main__':
    main()
