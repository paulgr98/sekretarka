import discord
from discord.ext import commands
from components import utility
from components import birthday_tracker as bt
import datetime as dt
import re


async def birthday_main(ctx: commands.Context, action: str, *args: str):
    if action == 'add':
        await process_add_birthday(ctx, *args)
    elif action == 'remove':
        await process_remove_birthday(ctx, *args)
    elif action == 'list':
        await list_all_birthdays(ctx)
    elif action == 'today':
        await list_today_birthdays(ctx)
    elif action == 'next':
        await list_nearest_birthdays(ctx)
    elif action == 'get':
        await get_birthday_of_user(ctx, *args)
    else:
        await ctx.reply('Niepoprawne użycie komendy. Możliwe akcj: add, remove, list, today, next, get')


async def get_user_and_date_from_args(ctx: commands.Context, *args: str):
    date = args[0]
    mention = args[1]
    user: discord.User = await utility.get_user_from_mention(ctx, mention)
    if user is None:
        await ctx.reply('Niepoprawne użycie komendy. Użyj: $bday add <data> <@user>')
        return None, None

    # check if date is in format dd.mm.yyyy
    if not re.search(r'\d{2}\.\d{2}\.\d{4}', date):
        await ctx.reply('Niepoprawny format daty. Użyj: dd.mm.yyyy (np. 05.05.2005)')
        return None, None

    return user, date


async def process_add_birthday(ctx: commands.Context, *args: str):
    if len(args) != 2:
        await ctx.reply('Niepoprawne użycie komendy. Użyj: !bday add <data> <@user>')
        return

    user, date = await get_user_and_date_from_args(ctx, *args)
    if user is None or date is None:
        return

    tracker = bt.BirthdayTracker()
    tracker.add_birthday(user.id, date)

    await ctx.reply(f'Dodano urodziny użytkownika {user.name} na dzień {date}')


async def process_remove_birthday(ctx: commands.Context, *args: str):
    if len(args) != 1:
        await ctx.reply('Niepoprawne użycie komendy. Użyj: !bday remove <@user>')
        return

    user = await utility.get_user_from_mention(ctx, args[0])
    if user is None:
        await ctx.reply('Niepoprawne użycie komendy. Użyj: !bday remove <@user>')
        return

    tracker = bt.BirthdayTracker()
    try:
        tracker.remove_birthday(user.id)
    except IndexError as e:
        await ctx.reply(str(e))
        return

    await ctx.reply(f'Usunięto urodziny użytkownika {user.name}')


async def list_all_birthdays(ctx: commands.Context):
    tracker = bt.BirthdayTracker()
    birthdays = tracker.get_all_birthdays()

    if len(birthdays) == 0:
        await ctx.reply('Brak urodzin do wyświetlenia')
        return

    message = 'Lista urodzin:\n'
    for user_id, date in birthdays.items():
        user = discord.utils.get(ctx.guild.members, id=int(user_id))
        if user is None:
            continue
        message += f'- {user.name}: {date}\n'

    await ctx.send(message)


async def get_today_birthdays() -> tuple[str, str] or None:
    tracker = bt.BirthdayTracker()
    today = dt.datetime.today().strftime('%d.%m.%Y')
    birthdays = tracker.get_birthdays_by_date(today)
    if len(birthdays) == 0:
        return None
    return birthdays


async def list_today_birthdays(ctx: commands.Context):
    birthdays = await get_today_birthdays()
    if birthdays is None:
        await ctx.reply('Dziś nikt nie ma urodzin')
        return

    message = 'Dziś urodziny mają:\n'
    message += get_birthdays_text(ctx, birthdays)

    await ctx.send(message)


async def list_nearest_birthdays(ctx: commands.Context):
    tracker = bt.BirthdayTracker()
    birthdays = tracker.get_nearest_upcoming_birthdays()

    if len(birthdays) == 0:
        await ctx.reply('Brak urodzin w tym roku')
        return

    message = 'Najbliższe urodziny mają:\n'
    message += get_birthdays_text(ctx, birthdays)

    await ctx.send(message)


def get_birthdays_text(ctx: commands.Context, birthdays: list[tuple[str, str]]) -> str:
    message = ''
    today = dt.datetime.today()
    for user_id, date in birthdays:
        user = discord.utils.get(ctx.guild.members, id=int(user_id))
        date = dt.datetime.strptime(date, '%d.%m.%Y')
        age = today.year - date.year
        message += f'- {user.name} ({age} lat)\n'
    return message


async def get_birthday_of_user(ctx: commands.Context, *args: str):
    if len(args) < 1:
        await ctx.reply('Niepoprawne użycie komendy. Użyj: $bday get <@user>')
        return

    mention = args[0]
    user: discord.User = await utility.get_user_from_mention(ctx, mention)
    if user is None:
        await ctx.reply('Niepoprawne użycie komendy. Użyj: $bday get <@user>')
        return

    tracker = bt.BirthdayTracker()
    birthday = tracker.get_birthday_by_id(str(user.id))
    if birthday is None:
        await ctx.reply(f'Nie znaleziono urodzin użytkownika {user.name}')
        return

    await ctx.reply(f'{user.name} ma urodziny {birthday}')
