import datetime as dt
import re

import discord
from discord.ext import commands

from bot import utility
from repositories.UserBirthDayByServerRepository import UserBirthDayByServerRepository


class BirthdayTracker:
    def __init__(self, db_connector, command_context: commands.Context):
        self.ctx = command_context
        self.bday_repo = UserBirthDayByServerRepository(db_connector)

    async def process(self, action: str, *args: str):
        if action == 'add':
            await self.process_add_birthday(*args)
        elif action == 'remove':
            await self.process_remove_birthday(*args)
        elif action == 'list':
            await self.list_all_birthdays()
        elif action == 'today':
            await self.list_today_birthdays()
        elif action == 'get':
            await self.get_birthday_of_user(*args)
        else:
            await self.ctx.reply('Niepoprawne użycie komendy. Możliwe akcje: add, remove, list, today, get')

    async def get_user_and_date_from_args(self, *args: str):
        date = args[0]
        mention = args[1]
        user: discord.User = await utility.get_user_from_mention(self.ctx, mention)
        if user is None:
            await self.ctx.reply('Niepoprawne użycie komendy. Użyj: $bday add <data> <@user>')
            return None, None

        # check if date is in format dd.mm.yyyy
        if not re.search(r'\d{2}\.\d{2}\.\d{4}', date):
            await self.ctx.reply('Niepoprawny format daty. Użyj: dd.mm.yyyy (np. 05.05.2005)')
            return None, None

        return user, date

    async def process_add_birthday(self, *args: str):
        if len(args) != 2:
            await self.ctx.reply('Niepoprawne użycie komendy. Użyj: !bday add <data> <@user>')
            return
        user, date = await self.get_user_and_date_from_args(*args)
        if user is None or date is None:
            return
        self.bday_repo.add_birthday(self.ctx.guild.id, user.id, date)
        await self.ctx.reply(f'Dodano urodziny użytkownika {user.display_name} na dzień {date}')

    async def process_remove_birthday(self, *args: str):
        if len(args) != 1:
            await self.ctx.reply('Niepoprawne użycie komendy. Użyj: !bday remove <@user>')
            return
        user = await utility.get_user_from_mention(self.ctx, args[0])
        if user is None:
            await self.ctx.reply('Niepoprawne użycie komendy. Użyj: !bday remove <@user>')
            return
        deleted: bool = self.bday_repo.delete_user_on_server(self.ctx.guild.id, user.id)
        if not deleted:
            await self.ctx.reply(f'Nie znaleziono urodzin użytkownika {user.display_name}')
            return
        await self.ctx.reply(f'Usunięto urodziny użytkownika {user.display_name}')

    async def list_all_birthdays(self):
        birthdays = self.bday_repo.get_all_birthdays_on_server(self.ctx.guild.id)
        if len(birthdays) == 0:
            await self.ctx.reply('Brak urodzin do wyświetlenia')
            return
        message = 'Lista urodzin:\n'
        for user_id, date in birthdays:
            user = discord.utils.get(self.ctx.guild.members, id=int(user_id))
            if user is None:
                continue
            message += f'- {user.display_name}: {date}\n'
        await self.ctx.send(message)

    async def get_today_birthdays(self) -> tuple[str, str] or None:
        today = dt.datetime.today().strftime('%d.%m.%Y')
        birthdays = self.bday_repo.get_birthday_for_date(self.ctx.guild.id, today)
        if len(birthdays) == 0:
            return None
        return birthdays

    async def list_today_birthdays(self):
        birthdays = await self.get_today_birthdays()
        if birthdays is None:
            await self.ctx.reply('Nikt nie ma dzisiaj urodzin')
            return
        message = 'Dziś urodziny mają:\n'
        message += self.get_birthdays_text(birthdays)
        await self.ctx.send(message)

    def get_birthdays_text(self, birthdays: list[tuple[str, str]]) -> str:
        message = ''
        today = dt.datetime.today()
        for user_id, date in birthdays:
            user = discord.utils.get(self.ctx.guild.members, id=int(user_id))
            date = dt.datetime.strptime(date, '%d.%m.%Y')
            age = today.year - date.year
            message += f'- {user.display_name} ({age} lat)\n'
        return message

    async def get_birthday_of_user(self, *args: str):
        if len(args) < 1:
            await self.ctx.reply('Niepoprawne użycie komendy. Użyj: $bday get <@user>')
            return

        mention = args[0]
        user: discord.User = await utility.get_user_from_mention(self.ctx, mention)
        if user is None:
            await self.ctx.reply('Niepoprawne użycie komendy. Użyj: $bday get <@user>')
            return

        birthday = self.bday_repo.get_birthday(self.ctx.guild.id, user.id)
        if birthday is None:
            await self.ctx.reply(f'Nie znaleziono urodzin użytkownika {user.display_name}')
            return

        await self.ctx.reply(f'{user.display_name} ma urodziny {birthday}')
