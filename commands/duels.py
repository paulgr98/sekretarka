import dataclasses
import datetime as dt
import enum
from enum import unique
from typing import Optional

import discord
from discord.ext import commands
from discord.ext import tasks

from bot import logger
from commands.dnd import dice


def get_timestamp() -> float:
    return dt.datetime.now(dt.timezone.utc).timestamp()


@unique
class DuelStatus(enum.Enum):
    PENDING = 0
    ACCEPTED = 1


@dataclasses.dataclass
class Duel:
    def __init__(self, ctx: commands.Context, opponent: discord.User,
                 timestamp: float = get_timestamp()):
        self.ctx = ctx
        self.player = ctx.author
        self.player_points = 0
        self.opponent = opponent
        self.opponent_points = 0
        self.status = DuelStatus.PENDING
        self.timestamp = timestamp

    def set_status(self, status: DuelStatus):
        self.status = status
        self.timestamp = get_timestamp()

    def __eq__(self, other):
        return ((self.player == other.player) and
                (self.opponent == other.opponent) and
                (self.status == DuelStatus.PENDING))

    def __str__(self):
        return f"{self.player.name} <-> {self.opponent.name}: {self.timestamp} ({self.status})"

    def __repr__(self):
        return (f"{self.player.name} [{self.player_points}] <-> {self.opponent.name} [{self.opponent_points}]: "
                f"{self.timestamp} ({self.status})")


class DuelQueue:
    def __init__(self):
        self.queue = []

    def add(self, duel: Duel):
        self.queue.append(duel)

    def remove(self, duel: Duel):
        self.queue.remove(duel)

    def exist(self, duel: Duel) -> bool:
        return duel in self.queue

    def get_duel(self, player: discord.User, opponent: discord.User) -> Optional[Duel]:
        duels = [duel for duel in self.queue if duel.player == player and duel.opponent == opponent]
        if len(duels) > 1:
            raise RuntimeError(f"Multiple duels found between {player} and {opponent}")
        return duels[0] if duels else None

    def get_active_duel(self, user: discord.User) -> Optional[Duel]:
        duels = [duel for duel in self.queue if
                 (duel.player == user or duel.opponent == user)
                 and duel.status == DuelStatus.ACCEPTED]
        if len(duels) > 1:
            raise RuntimeError(f"Multiple duels found for user {user}")
        return duels[0] if duels else None

    def get_player_duels(self, player: discord.User) -> Optional[list[Duel]]:
        duels = [duel for duel in self.queue if duel.player == player]
        return duels if duels else None

    def get_opponent_duels(self, opponent: discord.User) -> Optional[list[Duel]]:
        duels = [duel for duel in self.queue if duel.opponent == opponent]
        return duels if duels else None

    def is_player_already_in_duel(self, player: discord.User) -> bool:
        return any(player == d.player and d.status == DuelStatus.PENDING for d in self.queue)

    def is_opponent_already_in_duel(self, opponent: discord.User) -> bool:
        return any(opponent == d.opponent and d.status == DuelStatus.PENDING for d in self.queue)

    def remove_and_get_expired_duels(self) -> list[Duel]:
        one_hour = 3600
        current_timestamp = get_timestamp()
        expired_duels = [duel for duel in self.queue if current_timestamp - duel.timestamp >= one_hour]
        self.queue = [duel for duel in self.queue if current_timestamp - duel.timestamp < one_hour]
        return expired_duels


class DuelManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.duel_queue = DuelQueue()
        self.cleanup_task.start()
        self.last_ctx = None

    async def make_duel(self, ctx: commands.Context, opponent: discord.User):
        player = ctx.author
        if self.duel_queue.is_player_already_in_duel(player):
            await ctx.reply("Jesteś już w trakcie pojedynku!")
            return
        if self.duel_queue.is_opponent_already_in_duel(player):
            await ctx.reply("Twój przeciwnik jest już w trakcie pojedynku!")
            return
        new_duel = Duel(ctx, opponent)
        if self.duel_queue.exist(new_duel):
            await ctx.reply("Taki pojedynek już istnieje. Co jest dziwne, bo nie powinno mieć miejsca :thinking:")
            return
        self.duel_queue.add(new_duel)
        self.last_ctx = ctx
        await ctx.send(f"{opponent.mention}! {new_duel.player.display_name} wyzywa Cię na pojedynek!\n"
                       f"Masz godzinę na akceptowanie za pomocą **{ctx.prefix}duel accept**, albo możesz "
                       f"stchórzyć i użyć **{ctx.prefix}duel reject**, aby odrzucić.")

    async def _get_pending_duel(self, user: discord.User, is_player: bool) -> Optional[Duel]:
        duels = (self.duel_queue.get_player_duels(user) if is_player
                 else self.duel_queue.get_opponent_duels(user))
        if not duels:
            return None

        pending_duels = [duel for duel in duels if duel.status == DuelStatus.PENDING]
        if not pending_duels:
            return None

        if len(pending_duels) > 1:
            user_type = "player" if is_player else "opponent"
            raise RuntimeError(f"Multiple pending duels for {user_type} "
                               f"{user.display_name}({user.name}): {pending_duels}")
        return pending_duels[0]

    async def get_duel_for_player(self, player: discord.User) -> Optional[Duel]:
        return await self._get_pending_duel(player, is_player=True)

    async def get_duel_for_opponent(self, opponent: discord.User) -> Optional[Duel]:
        return await self._get_pending_duel(opponent, is_player=False)

    async def _get_duel_for_opponent_response(self, ctx: commands.Context) -> Optional[Duel]:
        opponent = ctx.author
        duel = await self.get_duel_for_opponent(opponent)
        if duel is None:
            await ctx.reply("Nie masz żadnego oczekującego pojedynku")
            return None
        return duel

    async def accept(self, ctx: commands.Context):
        duel = await self._get_duel_for_opponent_response(ctx)
        if not duel:
            return

        duel.set_status(DuelStatus.ACCEPTED)
        await ctx.send(f"{ctx.author.mention} przyjął wyzwanie od {duel.player.mention}!\n"
                       f"Niech obaj gracze użyją {ctx.prefix}duel roll")

    async def reject(self, ctx: commands.Context):
        duel = await self._get_duel_for_opponent_response(ctx)
        if not duel:
            return

        self.duel_queue.remove(duel)
        await ctx.send(f"{ctx.author.display_name} odrzucił wyzwanie of {duel.player.display_name}")

    async def roll(self, ctx: commands.Context):
        duel = self.duel_queue.get_active_duel(ctx.author)
        if not duel:
            await ctx.reply("Nie jesteś w trakcie żadnego pojedynku")
            return

        dnd_dice = dice.DndDice(ctx)
        result: dice.DnDDiceResult = await dnd_dice.roll("1d20")

        is_player = ctx.author == duel.player
        points = duel.player_points if is_player else duel.opponent_points

        if points > 0:
            await ctx.reply("Możesz rzucić tylko raz, cwaniaku")
            return

        if is_player:
            duel.player_points = result.total
        else:
            duel.opponent_points = result.total

        await ctx.reply(f"Wypadło {result.total}!")

        if self.does_both_players_rolled(duel):
            await self.send_results(duel)
            self.duel_queue.remove(duel)

    @classmethod
    def does_both_players_rolled(cls, duel: Duel) -> bool:
        return duel.player_points > 0 and duel.opponent_points > 0

    async def send_results(self, duel: Duel):
        winner = self.get_winner(duel)
        if winner:
            await self.last_ctx.channel.send(f"Wygrywa {winner.mention}! Gratulacje!")
        else:
            await self.last_ctx.channel.send("Wygląda na to, że mamy remis :kanna_poggers:")

    @classmethod
    def get_winner(cls, duel: Duel) -> Optional[discord.User]:
        if duel.player_points > duel.opponent_points:
            return duel.player
        elif duel.player_points < duel.opponent_points:
            return duel.opponent
        else:
            return None

    @tasks.loop(minutes=5)
    async def cleanup_task(self):
        expired_duels = self.duel_queue.remove_and_get_expired_duels()
        if expired_duels and self.last_ctx:
            for duel in expired_duels:
                try:
                    await self.last_ctx.channel.send(
                        f"Pojedynek między {duel.player.mention} a {duel.opponent.mention} "
                        f"został anulowany z powodu przekroczenia czasu oczekiwania."
                    )
                except Exception as e:
                    logger.logger.error(e)

    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    cog = DuelManager(bot)
    await bot.add_cog(cog)


def main():
    timestamp = get_timestamp()
    timestamp2 = timestamp + 3721
    print(timestamp)
    print(timestamp2)
    print(timestamp2 - timestamp)


if __name__ == "__main__":
    main()
