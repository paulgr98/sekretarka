import datetime as dt
import math
import random
import time
from threading import Thread
from typing import cast, Union

from bot.database.DbConnector import DbConnector
from config import DbConfig

db_connector = DbConnector(keyspace=DbConfig.DB_KEYSPACE, contact_points=DbConfig.DB_CONTACT_POINTS,
                           username=DbConfig.DB_USERNAME, password=DbConfig.DB_PASSWORD, port=DbConfig.DB_PORT)

import discord
from discord.ext import commands
from openai import RateLimitError, APIConnectionError
import asyncio
from bot import help
from bot import utility as util
from bot.UserConfigLoader import UserConfigLoader
from bot.logger import logger
from commands import alco_drink
from commands import meal_command
from commands import birthday_tracker as bt
from commands import converter
from commands import f1cmd
from commands import free
from commands import poll
from commands import smart_light as sl
from commands import text_to_speach as tts
from commands import weather
from commands.duels import DuelManager
from commands.casino.money import MoneyManager
from commands.casino import roulette as roulette_cmd
from commands.dnd import coin as dnd_coin
from commands.dnd import dice as dnd_dice
from components import (
    nameday as nd,
    tenor,
    epic_free_games as epic,
    essa,
    magic_ball,
    pp_len,
    morning_routine as mr,
    random_yt,
    f1 as f1schedule,
    astrology_api as astro_api
)
from components.compliments import get_compliment_list
from components.demotes import get_demotes
from components.disses import get_diss_list
from components.gpt_chat_history import ChatHistory, Message, GptRole
from components.openai_models import ChatGPT4Free, run_api
from components.reddit import get_subreddit_random_hot, SubredditOver18
from components.shipping import ShippingService
from components.uwuify import uwuify
from config import config as cfg

config_loader = UserConfigLoader()
config_loader.load('config/user_config.json')
user_config = config_loader.get_config()
COOLDOWN = user_config.general_channel_cooldown_time

# bot instance
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot_client = commands.Bot(command_prefix=user_config.bot_command_prefix, intents=intents)
bot_client.remove_command('help')

users_chat_history = ChatHistory()

error_messages = {
    'no_permission': 'Nie masz uprawnień do tej komendy',
    'wrong_coordinates': 'Niepoprawne współrzędne'
}

DISCORD_MESSAGE_LEN_LIMIT = 2000


# ----------------------------------------------------------------------------------------------------------------------

# handle errors
@bot_client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(f'Nie ma takiej komendy. Wpisz {bot_client.command_prefix}pomoc, żeby wyświetlić listę komend')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'Brak argumentu. Wpisz {bot_client.command_prefix}pomoc, żeby wyświetlić listę komend')
    elif isinstance(error, commands.CommandOnCooldown):
        time_left = error.retry_after
        if time_left > COOLDOWN:
            time_left = str(math.ceil(time_left / (COOLDOWN if COOLDOWN > 0 else 1))) + ' min'
        else:
            time_left = str(int(time_left)) + ' sek'
        await ctx.reply(f'Ta komenda posiada cooldown. Spróbuj znowu za {time_left}')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply(error_messages['no_permission'])
    elif isinstance(error, commands.BadArgument):
        await ctx.reply(f'Niepoprawne argumenty. Wpisz {bot_client.command_prefix}pomoc, żeby wyświetlić listę komend')
    else:
        logger.error(error)
        await ctx.reply('Error! Insert kremówka! <a:jp2:985844814597742683>')


# print message that the bot is ready
@bot_client.event
async def on_ready():
    print('Logged in as')
    print(bot_client.user)
    print('-----------------')
    print('Ready to go!')

    loaded_cogs = [cog for cog in bot_client.cogs]
    logger.info(f"Loaded cogs: {loaded_cogs}")

    tasks = [
        mr.schedule_morning_routine(bot_client, db_connector),
        f1schedule.schedule_f1_notifications(bot_client)
    ]
    await asyncio.gather(*tasks)


# on message convert content to lowercase
@bot_client.event
async def on_message(message):
    global user_config
    owner = user_config.owner
    co_owner = user_config.co_owner
    if message.author == bot_client.user:
        return
    if message.content.startswith(bot_client.command_prefix):
        # lower only the first part of the message
        head = message.content.split(' ')[0]
        tail = message.content.split(' ')[1:]
        message.content = head.lower() + ' ' + ' '.join(tail)
        await bot_client.process_commands(message)
    if owner.is_busy and f'<@{owner.id}>' in message.content:
        await message.channel.reply('Prezes Pajonk obecnie jest zajęty. Spróbuj później')
    if co_owner.is_busy and f'<@{co_owner.id}>' in message.content:
        await message.channel.reply('Pani Prezes obecnie jest zajęta. Spróbuj później')


# simple ping command
@bot_client.command()
async def ping(ctx):
    await ctx.reply('Pong!')


# simple hi command
@bot_client.command()
async def hi(ctx):
    global user_config
    if ctx.author.name == user_config.owner.nick:
        await ctx.reply('Hej przystojniaku :smirk:')
        return
    await ctx.reply(f'Hej {ctx.author.mention}!')


# get user's avatar in embed
@bot_client.command()
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed_title = f'{member.display_name}'
    if member.name != member.display_name:
        embed_title += f' ({member.name})'
    embed = discord.Embed(title=embed_title, color=0x328CED)
    embed.set_image(url=member.display_avatar.url)
    await ctx.reply(embed=embed)


# deleting given amount of messages above
@bot_client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount=1):
    if amount <= 50:
        await ctx.channel.purge(limit=amount + 1)
    else:
        await ctx.reply('Nie możesz usunąć więcej niż 50 jednocześnie')


# deleting given amount of messages reply by the bot
@bot_client.command()
async def undo(ctx, amount=1):
    await ctx.channel.purge(limit=1)
    # get last 200 messages
    # messages = await ctx.channel.history(limit=200).flatten() # flatten() removed
    messages = [msg async for msg in ctx.channel.history(limit=200)]
    # filter messages where the client is the bot
    messages = [m for m in messages if m.author == bot_client.user]
    # limit the messages to the given amount
    messages = messages[:amount]
    # delete messages
    await ctx.channel.delete_messages(messages)


# compliment command that reply one random compliment from predefined list
@bot_client.command()
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
async def compliment(ctx, member=None):
    global user_config
    if ctx.channel.name in user_config.bot_channel_names:
        compliment.reset_cooldown(ctx)
    # check for female_role role in user's roles to check if the user is a female
    if member is None:
        is_female = await is_current_user_female(ctx)
        # get compliment list
        compliments = get_compliment_list(ctx.author.display_name, is_female)
        await ctx.reply(random.choice(compliments))
        return

    # try cast member to discord.Member
    try:
        member_converter = commands.MemberConverter()
        member = await member_converter.convert(ctx, member)
    except commands.BadArgument:
        pass

    if isinstance(member, discord.Member):
        is_female = await is_user_female(member)
        name = member.display_name
        mention = member.mention
    else:
        is_female = str(member).endswith("a")
        name = member
        mention = member
    compliments = get_compliment_list(name, is_female)
    await ctx.reply(f'Komplement dla {mention}:\n{random.choice(compliments)}')


async def is_current_user_female(ctx: commands.Context) -> bool:
    global user_config
    is_female = await is_user_female(ctx.author)
    return is_female


# diss command that reply one random diss from predefined list
@bot_client.command()
@commands.cooldown(1, COOLDOWN, commands.BucketType.channel)
async def diss(ctx, member=None):
    global user_config
    if ctx.channel.name in user_config.bot_channel_names:
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
        is_female = util.has_roles(user_config.female_roles, ctx.author)
    else:
        is_female = False
    disses = get_diss_list(member, is_female)
    await ctx.reply(random.choice(disses))


# the opposite of motivate command
@bot_client.command()
async def demote(ctx):
    texts = get_demotes()
    await ctx.reply(random.choice(texts))


# get random post from given subreddit
@bot_client.command()
async def rdt(ctx, subreddit: str = 'memes', limit: int = 50):
    global user_config
    post = None
    try:
        is_channel_nsfw: bool = str(ctx.channel.name).lower() in user_config.nsfw_channel_names
        post = await get_subreddit_random_hot(subreddit, is_channel_nsfw, limit)
    except SubredditOver18 as e:
        # if channel is not nsfw, reply message
        if str(ctx.channel.name).lower() not in user_config.nsfw_channel_names:
            await ctx.reply(e)
            return
    except commands.CommandError as e:
        await ctx.reply(e)
        return

    title = post['title']
    # if title is too long, cut it
    if len(title) > 250:
        title = title[:250] + '...'
    embed = discord.Embed(title=title, color=0xFF5700)
    embed.set_author(name=post['author'])
    embed.set_image(url=post['url'])
    await ctx.reply(embed=embed)


# uwuify the message above
@bot_client.command()
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
@bot_client.command()
async def ban(ctx, member: discord.Member):
    global user_config
    # if there are more than 5 people to ban, remove the oldest one
    if len(to_ban) > 5:
        del to_ban[min(to_ban, key=to_ban.get)]
    if member.name == user_config.owner.nick:
        await ctx.reply('Nie masz tu mocy :sunglasses:')
        return
    if member.id == bot_client.user.id:
        await ctx.reply('Tylko buk może mnie sondzić!')
        return
    if member.id == ctx.author.id:
        message = await ctx.reply(
            f'Tego chcesz? xD Spoko. 2 :heart: pod tą wiadomością i banujemy {ctx.author.mention}')
        to_ban[message.id] = member
        return
    message = await ctx.reply(f'5 ❤ pod tą wiadomością i banujemy {member.mention}!')
    to_ban[message.id] = member


# if reaction is added to the ban message, count the heart reactions
@bot_client.event
async def on_reaction_add(reaction, user):
    if user == bot_client.user:
        return
    # get the message from reaction
    message = reaction.message

    # if the message is found in to_ban, ban the member
    if message.id in to_ban:
        member = to_ban[message.id]
        if '5 ❤ pod tą wiadomością i banujemy' in message.content and message.author.bot is True:
            if reaction.emoji == str("\u2764\ufe0f") and reaction.count == 5:
                await message.channel.reply(f'No i banujemy {member.mention}!')
        elif '2 ❤ pod tą wiadomością i banujemy' in message.content and message.author.bot is True:
            if reaction.emoji == str("\u2764\ufe0f") and reaction.count == 2:
                await message.channel.reply(f'No i banujemy {member.mention}! Na własne życzenie xD')


@bot_client.command('zw')
async def im_busy(ctx):
    global user_config
    owner = user_config.owner
    co_owner = user_config.co_owner
    if ctx.author.name == owner.nick:
        owner.is_busy = not owner.is_busy
        if owner is None:
            owner = ctx.author
        if owner.is_busy:
            await ctx.reply('Prezes Pajonk wychodzi na ważne spotkanie')
        else:
            await ctx.reply('Prezes Pajonk właśnie wrócił!')
    elif ctx.author.name == co_owner.nick:
        co_owner.is_busy = not co_owner.is_busy
        if co_owner is None:
            co_owner = ctx.author
        if co_owner.is_busy:
            await ctx.reply('Pani Prezes wychodzi na ważne spotkanie')
        else:
            await ctx.reply('Pani Prezes właśnie wróciła!')


# command to find gf or bf for the user
@bot_client.command()
async def shipme(ctx):
    global user_config
    # get list of all users in the server
    users = ctx.guild.members
    # try to get user from already existing list for today
    service = ShippingService(db_connector)
    ship_id = service.get_users_match_for_today(str(ctx.guild.id), str(ctx.author.id))
    if ship_id is not None:
        ship = bot_client.get_user(int(ship_id))
        await ctx.reply(f'{ctx.author.mention} myślę, że najlepszy ship na dzisiaj dla Ciebie to... {ship.mention}!')
        return

    # get list of users with role female_role
    females = []
    for u in users:
        user_roles = [r.name.lower() for r in u.roles]
        if await is_user_female(u) and 'bot' not in user_roles:
            females.append(u)

    if len(females) == 0:
        await ctx.reply('Error, brak dziewuch :/')
        return

    males = []
    for u in users:
        user_roles = [r.name for r in u.roles]
        if u not in females and 'bot' not in user_roles:
            males.append(u)

    if len(males) == 0:
        await ctx.reply('Error, brak chłopów :/')

    # if message author is in females, ship with males
    if ctx.author in females:
        ship = random.choice(males)
    else:
        ship = random.choice(females)
    # save ship to file
    service.save_users_match_for_today(ctx.guild.id, ctx.author.id, ship.id)
    await ctx.reply(f'{ctx.author.mention} myślę, że najlepszy ship na dzisiaj dla Ciebie to... {ship.mention}!')


async def is_user_female(user: discord.Member):
    global user_config
    is_female = util.has_roles(user_config.female_roles, user)
    return is_female


# command to get daily horoscopes for the user
@bot_client.command()
async def astro(ctx, sign: str):
    global user_config
    try:
        maker = astro_api.HoroscopeMaker()
        embed = maker.make_horoscope(sign).translate().get_embed()
        await ctx.reply(embed=embed)
    except astro_api.NoHoroscopeSignException as exc:
        await ctx.reply(exc)
    except ValueError:
        await ctx.reply("Coś się... coś się popsuło i nie było mnie słychać...")


# command to check for name days
@bot_client.command()
async def nameday(ctx):
    names = nd.get_names()
    today = dt.datetime.now().strftime('%d.%m.%Y')
    name_string = ', '.join(names) if names else 'nie wiem, bo coś się zepsuło'
    embed = discord.Embed(title=f'Imieniny na dzień {today}', color=0x4CC2F5)
    embed.add_field(name='Imieniny obchodzą: ', value=name_string, inline=False)
    await ctx.reply(embed=embed)


# command to get weather forecast for the given city
@bot_client.command()
async def wthr(ctx, city: str = 'Warszawa', days: int = 0):
    global user_config
    if ctx.channel.name not in user_config.bot_channel_names:
        await ctx.reply(f'komendy {bot_client.command_prefix}wthr można używać tylko na kanale do tego przeznaczonym')
        return

    if days > 4:
        await ctx.reply('Pogodę można sprawdzić maksymalnie na 4 dni')
        return

    try:
        embed = weather.make_weather_embed(city, days)
        await ctx.reply(embed=embed)
    except weather.WeatherException as e:
        await ctx.reply(e)


# command to get random number between given range
@bot_client.command('roll')
async def roll(ctx, code: str):
    if code is None or code == '':
        await ctx.reply('Rzucam 1D20...')
        code = '1d20'
    dice = dnd_dice.DndDice(ctx)
    await dice.roll_command(code)


# command to throw a coin
@bot_client.command(aliases=['flip'])
async def coin(ctx):
    await dnd_coin.coin(ctx)


# dictionary to save user id and their start time
stopwatch_dict = {}


# simple stopwatch command to measure time
@bot_client.command(aliases=['sw'])
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


@bot_client.command('poll')
async def create_poll(ctx, *, content: str):
    # remove whitespaces from the beginning and end of the string
    content = content.strip()
    # if the string is empty, return
    if not content:
        await ctx.reply('Nie wpisałeś treści')
        return
    # if the string is too long, return
    if len(content) > 250:
        await ctx.reply('Za długa treść')
        return

    # replace whitespaces before and after ; sign
    content = content.replace('; ', ';')
    content = content.replace(' ;', ';')

    # separate the content into question and options (separated by ';')
    content_list = content.split(';')
    question = poll.init_cap(content_list[0])
    options = content_list[1:]

    if 2 > len(options) > 10:
        await ctx.reply('Możliwa ilość odpowiedzi to od 2 do 10')
        return

    embed, reactions = poll.create_embed(question, options)

    msg = await ctx.reply(embed=embed)
    # add reactions to the message
    for reaction in reactions:
        await msg.add_reaction(reaction)


@bot_client.command('essa')
async def calc_essa(ctx, *, member=None):
    if member is None:
        member = ctx.author

    # if member is instance of discord.Member
    if isinstance(member, discord.Member):
        nickname = member.name
    else:
        nickname = member

    essa_level = essa.calculate_essa_level(nickname)
    await ctx.reply(f'{nickname} ma {essa_level}% essy')


# command to get a random cocktail recipe or search for a specific one form thecocktaildb.com
@bot_client.command()
async def drink(ctx: commands.Context, *drink_name: str):
    name = ' '.join(drink_name)
    embed = alco_drink.make_drink_embed(name)
    if embed is None:
        await ctx.reply('Nie znaleziono drinka :/')
        return
    await ctx.reply(embed=embed)


@bot_client.command()
async def meal(ctx: commands.Context, *args: str):
    meal_cmd = meal_command.MealCommand(ctx)
    if len(args) == 0:
        options = meal_command.get_options()
        await ctx.reply(options)
        return
    if "--list" in args:
        response = await meal_cmd.list_filter_options()
        await ctx.reply(response)
        return
    random_meal = await meal_cmd.get_embed(*args)
    if random_meal is None:
        await ctx.reply('Nie znaleziono posiłku, musisz głodować')
        return
    await ctx.reply(embed=random_meal)


# free epic store games
@bot_client.command('free')
async def epic_free_games(ctx: commands.Context, period: str = 'current'):
    global user_config
    if ctx.channel.name not in user_config.bot_channel_names:
        await ctx.reply(f'Komendy {bot_client.command_prefix}free można używać tylko na kanale do tego przeznaczonym')
        return
    try:
        free_games = epic.get_free_games(period)
    except ValueError:
        await ctx.reply('Niepoprawny okres. Możliwe wartości: current, upcoming')
        return
    for game in free_games:
        embed = free.make_game_embed(game, period)
        await ctx.reply(embed=embed)


async def reply_gif(ctx: commands.Context, *search_query: str, is_random: bool = True):
    query = ' '.join(search_query)
    ten = tenor.Tenor()
    gif = ten.get_gif(query, random=is_random)
    if gif is None or gif == '':
        await ctx.reply(f'{ctx.author.mention}, nie znaleziono GIFa :/')
        return
    await ctx.reply(f'{ctx.author.mention} {gif}')


@bot_client.command('gif')
async def reply_random_gif(ctx: commands.Context, *search_query: str):
    await reply_gif(ctx, *search_query, is_random=True)


@bot_client.command('topgif')
async def reply_top_gif(ctx: commands.Context, *search_query: str):
    await reply_gif(ctx, *search_query, is_random=False)


@bot_client.command('convert')
async def convert(ctx: commands.Context, method: str, *args: str):
    text = ' '.join(args)
    result = converter.convert(method, text)
    await ctx.reply(result)


@bot_client.command('8ball')
async def eight_ball(ctx: commands.Context):
    answer = magic_ball.get_random_answer()
    await ctx.reply(answer)


@bot_client.command('pp')
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
@bot_client.command('story')
async def story(ctx: commands.Context, *keywords: str):
    global user_config
    if ctx.channel.name not in user_config.bot_channel_names:
        await ctx.reply(f'Komendy {bot_client.command_prefix}story można używać tylko na kanale do tego przeznaczonym')
        return
    # check if there are any keywords
    if len(keywords) == 0:
        await ctx.reply('Podaj słowo kluczowe (np. kot)')
        return
    prompt = ' '.join(keywords)
    prompt = 'Napisz krótką historyjkę ' + prompt
    await gpt_command(ctx, prompt, False)


@bot_client.command(aliases=['rr', 'roulette'])
async def roulette_command(ctx: commands.Context, *args: str):
    global user_config
    if ctx.channel.name not in user_config.bot_channel_names:
        await ctx.reply('Tej komendy można używać tylko na kanale do tego przeznaczonym')
        return
    roulette_cmd_instance = roulette_cmd.RouletteCommand(ctx, db_connector)
    await roulette_cmd_instance.process(*args)


@bot_client.command('money')
async def money_command(ctx: commands.Context, *args: str):
    money_manager = MoneyManager(db_connector, ctx)
    await money_manager.process(*args)


@bot_client.command('morning')
@commands.has_permissions(administrator=True)
async def morning_routine_command(ctx: commands.Context, action: str = None, channel: discord.TextChannel = None):
    bad_usage_text = f"Poprawne użycie komendy to: {bot_client.command_prefix}morning [add|remove] <#kanal_tekstowy>"

    # Case 1: reply the morning message if no action is provided
    if not action and not channel:
        await mr.morning_routine_single(ctx, db_connector)
        return

    # Case 2: Validate action parameter
    if action not in ['add', 'remove']:
        await ctx.reply(bad_usage_text)
        return

    # Ensure the channel is provided and is a valid text channel
    if not channel or not isinstance(channel, discord.TextChannel):
        await ctx.reply("Musisz podać poprawny kanał tekstowy.")
        return

    # Case 3: Handle adding a channel to the morning routine
    if action == 'add':
        success = await mr.add_channel_to_morning_routine(db_connector, channel)
        if success:
            await ctx.reply(f'Kanał {channel.mention} został dodany do listy kanałów do rannych wiadomości.')

    # Case 4: Handle removing a channel from the morning routine
    elif action == 'remove':
        success = await mr.remove_channel_from_morning_routine(db_connector, channel)
        if success:
            await ctx.reply(f'Kanał {channel.mention} został usunięty z listy kanałów do rannych wiadomości.')


@bot_client.command('bday')
async def birthday_command(ctx: commands.Context, action: str, *args: str):
    tracker = bt.BirthdayTracker(db_connector, ctx)
    await tracker.process(action, *args)


@bot_client.command('gpt')
async def gpt_command(ctx: commands.Context, *args: str, include_msg_history: bool = True):
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
                response_task = asyncio.create_task(
                    gpt.complete(prompt, include_msg_history=include_msg_history)
                )
            else:
                response_task = asyncio.create_task(
                    gpt.complete(prompt, previous_messages, include_msg_history=include_msg_history)
                )
            response = (await response_task).choices[0].message.content
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
    # if response is longer than Discord limit, reply it in chunks
    users_chat_history.add(ctx.author.id, Message(prompt, GptRole.USER))
    if len(response) > DISCORD_MESSAGE_LEN_LIMIT:
        response_chunks = util.split_into_chunks(response, DISCORD_MESSAGE_LEN_LIMIT)
        for chunk in response_chunks:
            chunk = clean_blackbox_provider_response(chunk)
            users_chat_history.add(ctx.author.id, Message(response, GptRole.ASSISTANT))
            await ctx.reply(chunk)
    else:
        # if there are no errors, add both messages to history
        response = clean_blackbox_provider_response(response)
        users_chat_history.add(ctx.author.id, Message(prompt, GptRole.USER))
        users_chat_history.add(ctx.author.id, Message(response, GptRole.ASSISTANT))
        await ctx.reply(response)


def clean_blackbox_provider_response(response: str):
    # if contains rv1$@$, get only the text after it
    if 'rv1$@$' in response:
        response = response.split('rv1$@$')[1]
    return response


def handle_gpt_args(ctx: commands.Context, *args: str, ):
    global users_chat_history
    if len(args) == 0:
        return 'Nie podano argumentów'
    if args[0] == '--clear':
        users_chat_history.clear(ctx.author.id)
        return 'Historia została wyczyszczona'
    return None


@bot_client.command('f1')
async def f1_command(ctx: commands.Context):
    embed = f1cmd.make_next_race_embed()
    await ctx.reply("Następny wyścig", embed=embed)


# help command to show all commands
@bot_client.command(aliases=['pomoc', 'help'])
async def help_command(ctx: commands.Context):
    global user_config
    if ctx.channel.name not in user_config.bot_channel_names:
        await ctx.reply('Tej komendy można używać tylko na kanale do tego przeznaczonym')
        return
    embeds = help.get_help_embed(bot_client.command_prefix)
    for embed in embeds:
        await ctx.reply(embed=embed)


@bot_client.command('ryt')
async def ryt_command(ctx: commands.Context):
    rand_id = random_yt.youtube_search()
    await ctx.reply(f'https://www.youtube.com/watch?v={rand_id}')


@bot_client.command('lights')
async def lights_command(ctx: commands.Context, *args: str):
    global user_config
    if len(args) == 0:
        await ctx.reply('Brak argumentów\n'
                        'Dostępne opcje: main, additional, status, wakeup')
        return
    if args[0] not in ['main', 'additional', 'status', 'wakeup']:
        await ctx.reply('Niepoprawny argument\n'
                        'Dostępne opcje: main, additional, status, wakeup')
        return
    if not util.has_roles(user_config.special_permission_roles, ctx.author):
        await ctx.reply(error_messages['no_permission'])
        return
    if args[0] == 'main':
        sl.switch_main_lights()
        await ctx.reply('Przełączono światła główne')
    if args[0] == 'additional':
        sl.switch_additional_lights()
        await ctx.reply('Przełączono światła dodatkowe')
    if args[0] == 'status':
        status = sl.get_status()
        await ctx.reply(status)
    if args[0] == 'wakeup':
        owner_member = await util.get_user_from_username(ctx, user_config.owner.nick)
        await ctx.reply(f'Budzimy {owner_member.mention}!')
        sl.wake_up()


@bot_client.command('tts')
async def text_to_speach_command(ctx: commands.Context, *args: str):
    tts_client = tts.TextToSpeach(bot_client)
    if len(args) == 0:
        await ctx.reply('Brak argumentów')
        return
    if args[0] == '--join':
        await tts_client.join_voice_channel(ctx)
        return
    if args[0] == '--leave':
        await tts_client.leave_voice_channel(ctx)
        return
    await tts_client.text_to_speach(ctx, ' '.join(args))


@bot_client.command()
async def duel(ctx: commands.Context, arg: Union[discord.User, str] = None):
    bad_command_use = (f"Poprawne użycie komendy to: "
                       f"{ctx.prefix}duel [@opponent | accept | reject | roll]")
    duel_manager = cast(DuelManager, bot_client.get_cog('DuelManager'))
    if duel_manager is None:
        raise RuntimeError("DuelManager not found")

    try:
        if arg is None:
            await ctx.reply(f"Poprawne użycie komendy to: "
                            f"{ctx.prefix}duel [@opponent | accept | reject | roll]")
            return
        if arg == bot_client.user:
            await ctx.reply("Ze mną i tak nie masz szans :sunglasses:")
            return
        if isinstance(arg, discord.User):
            if arg == ctx.author:
                await ctx.reply("Sam ze sobą chcesz się pojedynkować? Jesteś głupi czy głupi?")
                return
            await duel_manager.make_duel(ctx, arg)
            return

        if not isinstance(arg, str):
            await ctx.reply(bad_command_use)
            return

        if arg == "accept":
            await duel_manager.accept(ctx)
        elif arg == "reject":
            await duel_manager.reject(ctx)
        elif arg == "roll":
            await duel_manager.roll(ctx)
        else:
            await ctx.reply(bad_command_use)

    except Exception as e:
        logger.error(f"Error in duel command: {e}")
        await ctx.reply("Ooopsie, Pawulon znowu coś zepsuł UwU")


async def connect_to_db():
    await db_connector.connect()


async def load_extensions():
    extensions = [
        "commands.duels"
    ]
    for extension in extensions:
        try:
            await bot_client.load_extension(extension)
            logger.info(f"Successfully loaded extension '{extension}'")
        except Exception as e:
            logger.error(f"Failed to load extension '{extension}': {e}")
            raise e


async def main():
    # run api on other thread
    api_thread = Thread(target=asyncio.run, args=(run_api(),))
    api_thread.start()

    try:
        await load_extensions()
        logger.info("All extensions loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load extensions: {e}")
        return

    # run main
    if user_config.enable_developer_mode:
        await bot_client.start(cfg.TOKEN_BETA)
    else:
        await bot_client.start(cfg.TOKEN)


if __name__ == '__main__':
    asyncio.run(connect_to_db())
    asyncio.run(main())
