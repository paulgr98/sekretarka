import asyncio
import random
import re

import discord
from discord.ext import commands

from bot.logger import logger


class CustomDiceError(Exception):
    pass


def get_random_number(max_value: int):
    return random.randint(1, max_value)


async def get_formatted_message(modifier, results, throws, total):
    results_str = ", ".join(map(str, results))
    if modifier >= 0:
        modifier_str = f"+{modifier}"
    else:
        modifier_str = str(modifier)
    msg = "Wyrzucono: "
    if throws == 1 and modifier == 0:
        msg += f"{results_str}"
    else:
        msg += f"({results_str}){modifier_str}"
        msg += f" = {total}"
    return msg


class DndDice(object):
    def __init__(self, ctx):
        self.pattern = r"(\d+)?d([1-9]\d*)([+-][1-9]\d*)?"
        self.context: discord.ext.commands.Context = ctx
        self.logger = logger
        self.DEFAULT_FACES = 20
        self.DEFAULT_THROWS = 1
        self.DEFAULT_MODIFIER = 0
        self.MAX_THROWS = 10
        self.MAX_FACES = 200
        self.MAX_MODIFIER = 100
        self.MIN_MODIFIER = -100

    def decode_pattern(self, code):
        result = re.match(self.pattern, code)
        if result:
            return result.groups()
        return None

    async def get_values(self, code):
        values = self.decode_pattern(code)
        if values is None:
            raise ValueError("Dice code does not match the pattern")

        throws, faces, modifier = values
        if throws is None or throws in ("", "0"):
            throws = self.DEFAULT_THROWS
        else:
            throws = int(throws)

        if faces is None:
            faces = self.DEFAULT_FACES
        else:
            faces = int(faces)

        if modifier is None:
            modifier = self.DEFAULT_MODIFIER
        else:
            modifier = int(modifier)

        return throws, faces, modifier

    async def show_error_message(self, msg=None):
        if msg is None:
            msg = ("Niepoprawny format kostki!\n"
                   "Upewnij się że format jest zgodny z oficjalnymi zasadami D&D")
        if self.context is not None:
            await self.context.reply(msg)
        else:
            logger.error(msg)

    async def show_message(self, msg):
        if self.context is not None:
            await self.context.reply(msg)
        else:
            logger.error(msg)

    def validate_values(self, throws, faces, modifier):
        if throws > self.MAX_THROWS:
            raise CustomDiceError(f"Za dużo rzutów! Maksymalnie {self.MAX_THROWS}")
        if faces > self.MAX_FACES:
            raise CustomDiceError(f"Za dużo ścian! Maksymalnie {self.MAX_FACES}")
        if not self.MAX_MODIFIER > modifier > self.MIN_MODIFIER:
            raise CustomDiceError(
                f"Zła wartość modyfikatora! Poprawnie między {self.MIN_MODIFIER} a {self.MAX_MODIFIER}")

    async def roll(self, code: str):
        try:
            throws, faces, modifier = await self.get_values(code)
            self.validate_values(throws, faces, modifier)

            if __name__ == "__main__":
                print(f"T:{throws}, F:{faces}, M:{modifier}")

            results = []
            for _ in range(throws):
                results.append(get_random_number(faces))

            total = sum(results) + modifier
            msg = await get_formatted_message(modifier, results, throws, total)

            await self.show_message(msg)


        except ValueError as exc:
            logger.error(exc)
            await self.show_error_message()
            return
        except CustomDiceError as exc:
            logger.error(exc)
            await self.show_error_message(str(exc))
            return


async def main():
    test_codes = [
        "d20",
        "1d20",
        "1d20+5",
        "1d20-5",
        "d20+5",
        "d20-5",
        "2d20",
        "2d20+5",
        "2d20-5",
        "1d6",
        "1d6+3",
        "1d6-3",
        "2d6",
        "2d6+3",
        "2d6-3",
        "d6",
        "d6+3",
        "d6-3",
        "0d6",
        "0d6+3",
        "0d6-3",
        "d6+0",
        "d6-0",
        "0d0",
        "0d0+0",
        "0d0-0",
        "d-10",
        "1d-10",
        "1d-10+5",
        "1d-10-5",
        "-1d10",
        "-1d10+5",
        "-1d10-5",
        "-1d-10",
        "-1d-10+5",
        "dupa",
        "dupaddupa"
        "dupa dupa dupa"
        "1 d 20",
        "100d20",
        "10d300",
        "10d20+200",
        "10d20-200",
    ]

    for code in test_codes:
        print(f"Testing code: {code}")
        dnd = DndDice(None)
        await dnd.roll(code)
        print()


if __name__ == "__main__":
    asyncio.run(main())
