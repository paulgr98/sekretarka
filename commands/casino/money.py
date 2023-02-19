import discord
from discord.ext import commands
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
    elif args[0] == 'remove':
        await process_remove_money(ctx, money_manager, *args)
    elif args[0] == 'ranking':
        await process_money_ranking(ctx, money_manager, client)
    else:
        await ctx.reply('Niepoprawny argument.\nMożliwe argumenty: check, claim, add, ranking')


async def process_add_money(ctx, money_manager, *args):
    # get list of user roles
    roles = [role.name for role in ctx.author.roles]
    if 'admin' in roles:
        if len(args) < 2:
            await ctx.reply('Nie podano kwoty')
            return
        if isinstance(int(args[1]), int):
            if 0 < int(args[1]) <= 1000:
                if len(args) == 3:
                    member = get_user_from_mention(ctx, args[2])
                    if member is None:
                        return
                    money_manager = money.MoneyManager(member.id)
                    money_manager.add_money(int(args[1]))
                else:
                    money_manager.add_money(int(args[1]))
            else:
                await ctx.reply('Podaj poprawną kwotę od 1 do 1000')
                return
            await ctx.reply(f'Dodano {args[1]} cebulionów')
        else:
            await ctx.reply('Podaj poprawną kwotę')
    else:
        await ctx.reply('Nie masz uprawnień do tej komendy')


async def process_remove_money(ctx, money_manager, *args):
    # get list of user roles
    roles = [role.name for role in ctx.author.roles]
    if 'admin' in roles:
        if len(args) == 3:
            await ctx.reply('Nie podano kwoty')
            return
        if isinstance(int(args[1]), int):
            if 0 < int(args[1]) <= 1000:
                if len(args) > 2:
                    member = get_user_from_mention(ctx, args[2])
                    if member is None:
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


async def get_user_from_mention(ctx: commands.Context, mention: str):
    try:
        # <@!user_id> -> user_id
        user_id = str(mention)[2:-1]
        # get user object from id
        member = discord.utils.get(ctx.guild.members, id=int(user_id))
        return member
    except ValueError:
        await ctx.reply('Podaj poprawny ID użytkownika')
        return None


async def process_money_ranking(ctx: commands.Context, money_manager: money.MoneyManager, client: commands.Bot):
    ranking = money_manager.get_ranking()
    msg_str: str = ''
    for user_id, amount in ranking:
        # find user by id
        user = await client.fetch_user(user_id)
        msg_str += f'{user.name} - {amount} cebulionów\n'
    await ctx.send(msg_str)
