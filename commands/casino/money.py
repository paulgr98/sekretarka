from discord.ext import commands

from bot import utility
from components.casino import money


def is_money_amount_valid(money_amount):
    return isinstance(int(money_amount), int)


class MoneyManager:
    def __init__(self, db_connector, command_context: commands.Context):
        self.daily_claim_amount = 1000
        self.ctx = command_context
        self.server_id = command_context.guild.id
        self.user_id = command_context.author.id
        self.money_service = money.MoneyService(db_connector=db_connector,
                                                default_daily_claim_amount=self.daily_claim_amount)

    async def process(self, *args: str):

        if len(args) == 0:
            await self.ctx.reply('Nie podano argumentów. \nDostępne argumenty: check, claim, add, ranking')
            return
        if args[0] == 'check':
            await self.ctx.reply(f'Masz {self.money_service.get_money(self.server_id, self.user_id)} cebulionów')
        elif args[0] == 'claim':
            if self.money_service.try_add_claim(self.server_id, self.user_id):
                await self.ctx.reply(f'Otrzymałeś {self.daily_claim_amount} cebulionów')
            else:
                await self.ctx.reply('Już otrzymałeś dziś darmowe pieniądze cebulaku!')
        elif args[0] == 'add':
            await self.__process_add_money__(*args)
        elif args[0] == 'give':
            await self.__process_give_money__(*args)
        elif args[0] == 'remove':
            await self.__process_remove_money__(*args)
        elif args[0] == 'ranking':
            await self.__process_money_ranking__()
        else:
            await self.ctx.reply('Niepoprawny argument.\nMożliwe argumenty: check, claim, add, ranking')

    async def __process_add_money__(self, *args):
        if not await self.__check_privileges__():
            await self.ctx.reply('Komenda dostępna tylko dla prezesa.\n'
                                 'Aby dostać darmowy hajs, wyślij prezesowi nudesy')
            return
        if len(args) < 2:
            await self.ctx.reply('Nie podano kwoty')
            return
        if isinstance(int(args[1]), int):
            if 0 < int(args[1]) <= 1000:
                money_amount = int(args[1])
                if len(args) == 3:
                    member = await utility.get_user_from_mention(self.ctx, args[2])
                    if member is None:
                        await self.ctx.reply('Podaj poprawny ID użytkownika')
                        return
                    self.money_service.add_money(self.server_id, member.id, money_amount)
                else:
                    self.money_service.add_money(self.server_id, self.user_id, money_amount)
            else:
                await self.ctx.reply('Podaj kwotę od 1 do 1000')
                return
            await self.ctx.reply(f'Dodano {money_amount} cebulionów')
        else:
            await self.ctx.reply('Podaj ilość cebulionów')

    async def __check_privileges__(self):
        # get list of user roles
        roles = [role.name for role in self.ctx.author.roles]
        if 'prezes' in roles:
            return True
        else:
            return False

    async def __process_give_money__(self, *args):
        money_arg = args[1]
        receiver_arg = args[2]

        if len(args) != 3:
            await self.ctx.reply('Zła ilość argumentów.\nPoprawne użycie: $money give <kwota> <@user>')
            return

        if not is_money_amount_valid(money_arg):
            await self.ctx.reply('Podaj poprawną kwotę')
            return

        money_amount = int(money_arg)
        if not 0 < money_amount <= 1000:
            await self.ctx.reply('Podaj poprawną kwotę od 1 do 1000')
            return

        sender_money = self.money_service.get_money(self.server_id, self.user_id)
        if sender_money < money_amount:
            await self.ctx.reply('Nie masz tyle pieniędzy')
            return

        receiver = await utility.get_user_from_mention(self.ctx, receiver_arg)
        if receiver is None:
            await self.ctx.reply('Podaj poprawny ID użytkownika')
            return

        self.money_service.subtract_money(self.server_id, self.user_id, money_amount)
        self.money_service.add_money(self.server_id, receiver.id, money_amount)
        await self.ctx.reply(f'Przekazano {money_amount} cebulionów dla {receiver.name}')

    async def __process_remove_money__(self, *args):
        money_arg = args[1]
        target_arg = args[2]

        roles = [role.name for role in self.ctx.author.roles]
        if 'admin' not in roles:
            await self.ctx.reply('Nie masz uprawnień do tej komendy')
            return

        if len(args) < 2:
            await self.ctx.reply('Nie podano kwoty')
            return

        if not is_money_amount_valid(money_arg):
            await self.ctx.reply('Podaj poprawną kwotę')
            return

        money_amount = int(money_arg)
        if not 0 < money_amount <= 1000:
            await self.ctx.reply('Podaj poprawną kwotę od 1 do 1000')
            return

        if len(args) > 2:
            target = await utility.get_user_from_mention(self.ctx, target_arg)

            if target is None:
                await self.ctx.reply('Podaj poprawny ID użytkownika')
                return

            self.money_service.subtract_money(self.server_id, target.id, money_amount)
        else:
            self.money_service.subtract_money(self.server_id, self.user_id, money_amount)

        await self.ctx.reply(f'Usunięto {args[1]} cebulionów')

    async def __process_money_ranking__(self):
        ranking = self.money_service.get_ranking(self.server_id)
        msg_str: str = ''
        for user_id, amount in ranking:
            # find user by id
            user = await utility.get_user_from_id(self.ctx, user_id)
            msg_str += f'{user.display_name} - {amount} cebulionów\n'
        if msg_str == '':
            await self.ctx.reply('Brak danych do wyświetlenia')
            return
        await self.ctx.send(msg_str)
