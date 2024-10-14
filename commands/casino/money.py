from discord.ext import commands

from bot import utility
from components.casino import money


async def money_command(ctx: commands.Context, client: commands.Bot, *args: str):
    money_manager = money.MoneyManager(ctx.author.id)
    if len(args) == 0:
        await ctx.reply('Nie podano argumentów. \nDostępne argumenty: check, claim, add, ranking')
        return
    if args[0] == 'check':
        await ctx.reply(f'Masz {money_manager.get_money()} cebulionów')
    elif args[0] == 'claim':
        if money_manager.claim_daily():
            await ctx.reply(f'Otrzymałeś {money_manager.daily_amount} cebulionów')
        else:
            await ctx.reply('Już otrzymałeś dziś darmowe pieniądze cebulaku!')
    elif args[0] == 'add':
        await process_add_money(ctx, money_manager, *args)
    elif args[0] == 'give':
        await process_give_money(ctx, money_manager, *args)
    elif args[0] == 'remove':
        await process_remove_money(ctx, money_manager, *args)
    elif args[0] == 'ranking':
        await process_money_ranking(ctx, money_manager, client)
    else:
        await ctx.reply('Niepoprawny argument.\nMożliwe argumenty: check, claim, add, ranking')


async def process_add_money(ctx, money_manager, *args):
    if not await check_privileges(ctx):
        await ctx.reply('Komenda dostępna tylko dla prezesa.\n'
                        'Aby dostać darmowy hajs, wyślij prezesowi nudesy')
        return
    if len(args) < 2:
        await ctx.reply('Nie podano kwoty')
        return
    if isinstance(int(args[1]), int):
        if 0 < int(args[1]) <= 1000:
            if len(args) == 3:
                member = await utility.get_user_from_mention(ctx, args[2])
                if member is None:
                    await ctx.reply('Podaj poprawny ID użytkownika')
                    return
                money_manager = money.MoneyManager(member.id)
                money_manager.add_money(int(args[1]))
            else:
                money_manager.add_money(int(args[1]))
        else:
            await ctx.reply('Podaj kwotę od 1 do 1000')
            return
        await ctx.reply(f'Dodano {args[1]} cebulionów')
    else:
        await ctx.reply('Podaj ilość cebulionów')


async def check_privileges(ctx: commands.Context):
    # get list of user roles
    roles = [role.name for role in ctx.author.roles]
    if 'prezes' in roles:
        return True
    else:
        return False


async def process_give_money(ctx, sender, *args):
    if len(args) != 3:
        await ctx.reply('Zła ilość argumentów.\nPoprawne użycie: $money give <kwota> <@user>')
        return
    if isinstance(int(args[1]), int):
        if 0 < int(args[1]) <= 1000:
            if sender.get_money() < int(args[1]):
                await ctx.reply('Nie masz tyle pieniędzy')
                return
            member = await utility.get_user_from_mention(ctx, args[2])
            if member is None:
                await ctx.reply('Podaj poprawny ID użytkownika')
                return
            sender.remove_money(int(args[1]))

            receiver = money.MoneyManager(member.id)
            receiver.add_money(int(args[1]))
            await ctx.reply(f'Przekazano {args[1]} cebulionów dla {member.name}')
        else:
            await ctx.reply('Podaj poprawną kwotę od 1 do 1000')
            return
    else:
        await ctx.reply('Podaj poprawną kwotę')


async def process_remove_money(ctx, money_manager, *args):
    # get list of user roles
    roles = [role.name for role in ctx.author.roles]
    if 'admin' in roles:
        if len(args) < 2:
            await ctx.reply('Nie podano kwoty')
            return
        if isinstance(int(args[1]), int):
            if 0 < int(args[1]) <= 1000:
                if len(args) > 2:
                    member = await utility.get_user_from_mention(ctx, args[2])
                    if member is None:
                        await ctx.reply('Podaj poprawny ID użytkownika')
                        return
                    money_manager = money.MoneyManager(member.id)
                    money_manager.remove_money(int(args[1]))
                else:
                    money_manager.remove_money(int(args[1]))
            else:
                await ctx.reply('Podaj poprawną kwotę od 1 do 1000')
                return
            await ctx.reply(f'Usunięto {args[1]} cebulionów')
        else:
            await ctx.reply('Podaj poprawną kwotę')
    else:
        await ctx.reply('Nie masz uprawnień do tej komendy')


async def process_money_ranking(ctx: commands.Context, money_manager: money.MoneyManager, client: commands.Bot):
    ranking = money_manager.get_ranking()
    msg_str: str = ''
    for user_id, amount in ranking:
        # find user by id
        user = await client.fetch_user(user_id)
        msg_str += f'{user.name} - {amount} cebulionów\n'
    await ctx.send(msg_str)
