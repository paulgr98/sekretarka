import discord
from discord.ext import commands
import config as cfg
from asyncprawcore import exceptions
import logging
import datetime as dt
import time
import random
import math


from components.uwuify import uwuify
from components.reddit import get_subreddit_random_hot
from components.demotes import get_demotes
from components.compliments import get_compliment_list
from components.disses import get_diss_list
from components.shipping import save_users_match_for_today, get_users_match_for_today, get_user_top_match
from components import nameday as nd
from components import tenor
from components import epic_free_games as epic

from commands import help
from commands import converter
from commands import free
from commands import drink
from commands import weather
from commands import astrology

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
class Usr:
    def __init__(self):
        self.is_busy = False
        self.user = None


owner = Usr()

bot_channels = ['bot']

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
    if ctx.author.name == 'PanPajonk':
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
    if member.name == 'PanPajonk':
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


@client.command()
async def zw(ctx):
    if ctx.author.name == 'PanPajonk':
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


search_running = False


# command to get top 5 inactive users in the server by their last message time
@client.command()
async def inactive(ctx):
    global search_running
    users_can_run = ['PanPajonk']
    if ctx.author.name not in users_can_run:
        await ctx.send('Nie masz uprawnień do tej komendy')
        return

    if search_running:
        await ctx.send('Już przeszukuję wiadomości, trochę cierpliwości...')
        return

    search_running = True
    await ctx.send('Ok, poczekaj (dłuższą) chwilę...')

    # get all users in the server
    users = ctx.guild.members
    users_id = [user.id for user in users]
    user_last_msg_time_dict = {}
    messages = [msg async for msg in ctx.channel.history(limit=50000)]
    # sort the messages by their timestamp from newest to oldest
    messages.sort(key=lambda x: x.created_at, reverse=True)

    for message in messages:
        # if user is not a bot, and is not yet in the dictionary
        # check if user is not yet in the dictionary and is still in the server
        if message.author.id not in user_last_msg_time_dict and message.author.id in users_id:
            # if the user is not a bot, add it to the dictionary
            user = message.author
            if not user.bot:
                user_last_msg_time_dict[message.author.id] = message.created_at

    # sort the users by their last message time from newest to oldest
    user_last_msg_time_dict = sorted(user_last_msg_time_dict.items(), key=lambda x: x[1])
    # get the top 5 users
    msg_str = ''
    for user_id, last_msg_time in user_last_msg_time_dict[:5]:
        user = client.get_user(user_id)
        msg_str += f'{user.name} - {last_msg_time.strftime("%d.%m.%Y %H:%M")}\n'

    embed = discord.Embed(title='Najmniej aktywni użytkownicy', color=0x571E1E)
    embed.add_field(name='TOP 5', value=msg_str, inline=False)
    search_running = False
    await ctx.send(embed=embed)


# command to create simple poll
@client.command()
async def poll(ctx, *, content: str):
    def init_cap(s):
        return s[0].upper() + s[1:]

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
    question = init_cap(content_list[0])
    options = content_list[1:]

    if len(options) < 2:
        await ctx.send('Za mało odpowiedzi (min 2)')
        return
    if len(options) > 10:
        await ctx.send('Za dużo odpowiedzi (max 10)')
        return

    # list of keycap numbers emojis for the options
    number_emojis = [f"{num}\N{COMBINING ENCLOSING KEYCAP}" for num in range(1, 10)]

    embed = discord.Embed(title=question, color=0x571E1E)
    opt_str = ''
    reactions = []

    # add the options to the embed
    for i, opt in enumerate(options):
        opt_str += f'{number_emojis[i]} {opt}\n'
        reactions.append(number_emojis[i])

    embed.add_field(name='Odpowiedzi', value=opt_str, inline=False)

    msg = await ctx.send(embed=embed)
    # add reactions to the message
    for reaction in reactions:
        await msg.add_reaction(reaction)


# command to check essa level of the user
@client.command()
async def essa(ctx, *, member=None):
    if member is None:
        member = ctx.author

    # try cast member to discord.Member
    if not isinstance(member, discord.Member):
        try:
            member_converter = commands.MemberConverter()
            member = await member_converter.convert(ctx, member)
        except commands.BadArgument:
            pass

    # if member is instance of discord.Member
    if isinstance(member, discord.Member):
        nickname = member.name
    else:
        nickname = member

    vowels = ['a', 'e', 'i', 'o', 'u']
    num_of_vowels = 0
    for letter in nickname:
        if letter in vowels:
            num_of_vowels += 1

    essa_level = (len(nickname) ** 69 + num_of_vowels) % 100
    await ctx.send(f'{nickname} ma {essa_level}% essy')


# command to get a random cocktail recipe or search for a specific one form thecocktaildb.com
@client.command()
async def drink(ctx: commands.Context, *drink_name: str):
    name = ' '.join(drink_name)
    embed = drink.make_drink_embed(name)
    if embed is None:
        await ctx.send('Nie znaleziono drinka :/')
        return
    await ctx.send(embed=embed)


# free epic store games
@client.command()
async def free(ctx: commands.Context, period: str = 'current'):
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


# help command to show all commands
@client.command()
async def pomoc(ctx: commands.Context):
    embed = help.get_help_embed(client.command_prefix)
    await ctx.send(embed=embed)


# run the bot
client.run(cfg.TOKEN)
