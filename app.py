import math

import discord
from discord.ext import commands
import config as cfg
import youtube_dl
from asyncprawcore import exceptions
import logging
# import streamrip
import os
import datetime as dt
import time
import requests
import random
import asyncio
from components.uwuify import uwuify
from components.weather import get_current_weather, get_x_day_forecast
from components.reddit import get_subreddit_random_hot
from components.demotes import get_demotes
from components.complements import get_complement_list
from components.disses import get_diss_list
from components.shipping import save_users_match_for_today, get_users_match_for_today, get_user_top_match
from googletrans import Translator
import components.nameday as nd

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


pajonk = Usr()

# logger config
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s at %(asctime)s]: %(message)s', '%d.%m %H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger('discord')
logger.addHandler(handler)

# astro API config
# https://rapidapi.com/sameer.kumar/api/aztro/
astro_api = "https://sameer-kumar-aztro-v1.p.rapidapi.com/"
astro_api_headers = {
    "X-RapidAPI-Key": cfg.RAPID_API_KEY,
}


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
    if pajonk.is_busy:
        if f'<@{pajonk.user.id}>' in message.content:
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
    messeges = await ctx.channel.history(limit=200).flatten()
    # filter messages where the client is the bot
    messages = [m for m in messeges if m.author == client.user]
    # limit the messeages to the given amount
    messages = messages[:amount]
    # delete messages
    await ctx.channel.delete_messages(messages)


# complement command that send one random complement from predefined list
@client.command()
@commands.cooldown(1, 300, commands.BucketType.channel)
async def complement(ctx, member=None):
    if ctx.channel.name in ('﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃', 'bot'):
        complement.reset_cooldown(ctx)
    # check for 'kobita' role in user's roles to check if the user is a female
    if member is None:
        is_female = 'kobita' in [role.name for role in ctx.author.roles]
        # get complement list
        complements = get_complement_list(ctx.author.name, is_female)
        await ctx.send(random.choice(complements))
        return

    # try cast member to discord.Member
    try:
        converter = commands.MemberConverter()
        member = await converter.convert(ctx, member)
    except commands.BadArgument:
        pass

    if isinstance(member, discord.Member):
        is_female = 'kobita' in [role.name for role in member.roles]
        name = member.name
        mention = member.mention
    else:
        is_female = False
        name = member
        mention = member
    complements = get_complement_list(name, is_female)
    await ctx.send(f'Komplement dla {mention}:\n{random.choice(complements)}')


# diss command that send one random diss from predefined list
@client.command()
@commands.cooldown(1, 300, commands.BucketType.channel)
async def diss(ctx, member=None):
    if ctx.channel.name in ('﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃', 'bot'):
        diss.reset_cooldown(ctx)
    # check for 'kobita' role in user's roles to check if the user is female
    if member is None:
        member = ctx.author

    # try cast member to discord.Member
    if not isinstance(member, discord.Member):
        try:
            converter = commands.MemberConverter()
            member = await converter.convert(ctx, member)
        except commands.BadArgument:
            pass

    # check if the member is instance of discord.Member
    if isinstance(member, discord.Member):
        is_female = 'kobita' in [role.name for role in member.roles]
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
    if ctx.channel.name not in ('﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃', 'bot'):
        await ctx.send(f'komendy {client.command_prefix}rdt można używać tylko na kanale ﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃')
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
    message = await ctx.channel.history(limit=2).flatten()
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
        pajonk.is_busy = not pajonk.is_busy
        if pajonk.user is None:
            pajonk.user = ctx.author
        if pajonk.is_busy:
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

    # get list of users with role 'kobita'
    females = []
    for u in users:
        roles = [r.name for r in u.roles]
        if 'kobita' in roles and 'bot' not in roles:
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
    if ctx.channel.name not in ('﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃', 'bot'):
        await ctx.send(f'komendy {client.command_prefix}astro można używać tylko na kanale ﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃')
        return

    sign = sign.lower()
    # signs dictonary with all signs in polish and their values in english
    sign_dict = {'baran': 'aries', 'byk': 'taurus', 'bliźnięta': 'gemini', 'rak': 'cancer', 'lew': 'leo',
                 'panna': 'virgo', 'waga': 'libra', 'skorpion': 'scorpio', 'strzelec': 'sagittarius',
                 'koziorożec': 'capricorn', 'wodnik': 'aquarius', 'ryby': 'pisces'}
    sign_dict_reversed = {v: k for k, v in sign_dict.items()}

    # check if the sign is in the dictonary
    if sign in sign_dict.keys():
        sign_eng = sign_dict[sign]
    else:
        awailable_signs = ', '.join(sign_dict.keys())
        await ctx.send(f'Nie ma takiego znaku \nDostępne znaki: \n{awailable_signs}')
        return

    # get the horoscope from the API
    querystring = {"sign": sign_eng, "day": "today"}
    response = requests.request("POST", astro_api, headers=astro_api_headers, params=querystring)

    # tramslate the horoscope to polish
    translator = Translator()
    description = response.json()['description']
    description_pl = translator.translate(description, src='en', dest='pl').text
    mood = response.json()['mood']
    mood_pl = f"{translator.translate(mood, src='en', dest='pl').text} ({mood})"
    color_pl = translator.translate(response.json()['color'], src='en', dest='pl').text
    comp = response.json()['compatibility'].lower()
    comp_pl = sign_dict_reversed[comp]

    # create the embed with the horoscope
    today = dt.datetime.now().strftime('%d.%m.%Y')
    embed = discord.Embed(title=f'{sign.upper()} {today}', color=0x5D37E6)
    embed.add_field(name='Opis', value=f'EN:\n{description}\n\nPL:\n{description_pl}', inline=False)
    embed.add_field(name='Kompatybilność', value=str(comp_pl).capitalize(), inline=False)
    embed.add_field(name='Szczęśliwa liczba', value=response.json()['lucky_number'], inline=False)
    embed.add_field(name='Nastrój', value=mood_pl, inline=False)
    embed.add_field(name='Kolor', value=color_pl, inline=False)

    await ctx.send(embed=embed)


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
    if ctx.channel.name not in ('﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃', 'bot'):
        await ctx.send(f'komendy {client.command_prefix}wthr można używać tylko na kanale ﹄𝕂𝕠𝕞𝕖𝕟𝕕𝕪﹃')
        return

    if days > 14:
        await ctx.send('Pogodę można sprawdzić maksymalnie na 14 dni')
        return

    # create dictionary for each day in polish and english
    day_dict = {"monday": "Poniedziałek", "tuesday": "Wtorek", "wednesday": "Środa", "thursday": "Czwartek",
                "friday": "Piątek", "saturday": "Sobota", "sunday": "Niedziela"}

    if days == 0:
        current_weather_json = get_current_weather(city)
        day_weather_json = get_x_day_forecast(city, days + 1)
        if current_weather_json['cod'] in ['404', '400'] or day_weather_json['cod'] in ['404', '400']:
            await ctx.send(f'Nie znaleziono miasta {city}')
            return

        # get the current date
        date = dt.datetime.now().strftime('%d.%m.%Y')
        # create day_of_week string from date
        day_of_week = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%A').lower()
        day_of_week_pl = day_dict[day_of_week]

        day = day_weather_json['list'][days]
        description = day["weather"][0]["description"].capitalize()
        temp = current_weather_json["main"]["temp"]
        temp_min = day["temp"]["min"]
        temp_max = day["temp"]["max"]
        feels_like = current_weather_json["main"]["feels_like"]
        pressure = day["pressure"]
        humidity = day["humidity"]
        sunset = current_weather_json["sys"]["sunset"]
        sunrise = current_weather_json["sys"]["sunrise"]
        sunrise = dt.datetime.fromtimestamp(sunrise).strftime('%H:%M')
        sunset = dt.datetime.fromtimestamp(sunset).strftime('%H:%M')

        embed = discord.Embed(title=f'Pogoda dla {city.title()}, {date} ({day_of_week_pl})', color=0x066FBF)
        embed.add_field(name='Opis', value=description, inline=False)
        embed.add_field(name='Temperatura', value=f'Aktualna: {float(temp):.1f} °C\n '
                                                  f'Odczuwalna: {float(feels_like):.1f} °C\n\n'
                                                  f'Maksymalna: {float(temp_max):.1f} °C\n'
                                                  f'Minimalna: {float(temp_min):.1f} °C', inline=False)
        embed.add_field(name='Ciśnienie', value=f'{pressure} hPa', inline=False)
        embed.add_field(name='Wilgotność', value=f'{humidity}%', inline=False)
        embed.add_field(name='Słońce', value=f'Wschód: {sunrise}\nZachód: {sunset}', inline=False)

    else:
        day_weather_json = get_x_day_forecast(city, days + 1)
        if day_weather_json['cod'] in ['404', '400']:
            await ctx.send(f'Nie znaleziono miasta {city}')
            return
        day = day_weather_json['list'][days]
        date = dt.datetime.fromtimestamp(day["dt"]).strftime('%d.%m.%Y')
        day_of_week = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%A').lower()
        day_of_week_pl = day_dict[day_of_week]
        description = day["weather"][0]["description"].capitalize()
        temp_min = day["temp"]["min"]
        temp_max = day["temp"]["max"]
        pressure = day["pressure"]
        humidity = day["humidity"]
        sunrise = dt.datetime.fromtimestamp(day["sunrise"]).strftime('%H:%M')
        sunset = dt.datetime.fromtimestamp(day["sunset"]).strftime('%H:%M')

        embed = discord.Embed(title=f'Pogoda dla {city.title()}, {date} ({day_of_week_pl})', color=0x066FBF)
        embed.add_field(name='Opis', value=description, inline=False)
        embed.add_field(name='Temperatura', value=f'Maksymalna: {float(temp_max):.1f} °C\n'
                                                  f'Minimalna: {float(temp_min):.1f} °C', inline=False)
        embed.add_field(name='Ciśnienie', value=f'{pressure} hPa', inline=False)
        embed.add_field(name='Wilgotność', value=f'{humidity}%', inline=False)
        embed.add_field(name='Słońce', value=f'Wschód: {sunrise}\nZachód: {sunset}', inline=False)

    await ctx.send(embed=embed)


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
        return


search_running = False


# command to get top 5 inactive users in the server by their last message time
@client.command()
async def inactive(ctx):
    global search_running
    if ctx.author.name not in ('PanPajonk', 'Leylalala', 'Kidler'):
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
    messages = await ctx.channel.history(limit=50000).flatten()
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
            converter = commands.MemberConverter()
            member = await converter.convert(ctx, member)
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


# help command to show all commands
@client.command()
async def pomoc(ctx):
    embed = discord.Embed(title="Pomoc", description="Lista komend", color=0x00ff00)
    embed.add_field(name=f"{client.command_prefix}ping",
                    value="Testuje połącznie",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}hi",
                    value="Wita się",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}purge [ilość=2]",
                    value="Usuwa [ilość] wiadomości wyżej. Domyślnie, bez podawania jawnie, ilość=2",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}undo [ilość=1]",
                    value="Usuwa [ilość] ostatnich wiadomości bota. Domyślnie, bez podawania jawnie, ilość=1",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}complement [użytkownik=None]",
                    value="Daje komplement użytkownikowi [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}demote",
                    value="Demotywuje do życia (jakby samo życie nie wystarczało)",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}rdt [sub=memes] [limit=100]",
                    value="Wyświetla losowy obrazek z reddita na subreddicie [sub], losując spośród [limit] "
                          "najpopularniejszych obrazków",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}astro [znak]",
                    value="Wyświetla horoskop dla znaku [znak]",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}nameday",
                    value="Wyświetla imieniny dla obecnego dnia",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}wthr [miasto=Warszawa] [dni=0]",
                    value="Wyświetla prognozę pogody dla miasta [miasto], za [dni] dni",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}shipme",
                    value="Wyświetla ship dla Ciebie",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}shipstat",
                    value="Wyświetla użytkownika, z którym masz największą liczbę shipów",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}roll [minimum=1] [maximum=6]",
                    value="Wyświetla losową liczbę między [minimum] a [maximum]",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}coin",
                    value="Rzuca monetą i wyświetla wynik (orzeł albo reszka)",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}sw [start/stop/reset]",
                    value="Uruchamia stoper, zatrzymuje go, lub resetuje",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}inactive",
                    value="Wyświetla TOP 5 najmniej aktywnych użytkowników",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}poll [treść]; [odp1]; [odp2]; ...",
                    value="Tworzy ankietę z podanych opcji. Treść i opcje muszą być oddzielone ;",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}essa [użytkownik=None]",
                    value="Wyświetla esse użytkownika [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}uwu",
                    value="UwUalizuje wiadomość wyżej",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}ban [użytkownik]",
                    value="Banuje użytkownika [użytkownik]",
                    inline=False)
    embed.add_field(name=f"{client.command_prefix}help",
                    value="Wyświetla listę komend",
                    inline=False)
    await ctx.send(embed=embed)


# run the bot
client.run(cfg.TOKEN)
