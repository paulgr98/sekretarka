import math

import discord


class HelpEmbedField(object):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class HelpEmbed(object):
    def __init__(self, limit: int = 20):
        self.fields = []
        self.limit = limit

    def add_field(self, name: str, value: str):
        self.fields.append(HelpEmbedField(name, value))

    def get_discord_embeds(self):
        # split fields into chunks of 20 into separate embeds
        chunks = math.ceil(len(self.fields) / self.limit)
        embeds = []
        for i in range(chunks):
            embed = discord.Embed(title=f"Pomoc {i + 1}/{chunks}", description="Lista komend", color=0x00ff00)
            if i == chunks - 1:
                for field in self.fields[i * self.limit:]:
                    embed.add_field(name=field.name, value=field.value, inline=False)
            else:
                for field in self.fields[i * self.limit:(i + 1) * self.limit]:
                    embed.add_field(name=field.name, value=field.value, inline=False)
            embeds.append(embed)
        return embeds


def get_help_embed(prefix: str) -> list[discord.Embed]:
    help_embed = HelpEmbed(15)

    help_embed.add_field(name=f"{prefix}ping",
                         value="Testuje połączenie")
    help_embed.add_field(name=f"{prefix}hi",
                         value="Wita się")
    help_embed.add_field(name=f"{prefix}avatar [użytkownik=None]",
                         value="Wyświetla avatar użytkownika [użytkownik] jeśli podany, lub autora, jeśli nie podany")
    help_embed.add_field(name=f"{prefix}purge [ilość=2]",
                         value="Usuwa [ilość] wiadomości wyżej. Domyślnie, bez podawania jawnie, ilość=2")
    help_embed.add_field(name=f"{prefix}undo [ilość=1]",
                         value="Usuwa [ilość] ostatnich wiadomości bota. Domyślnie, bez podawania jawnie, ilość=1")
    help_embed.add_field(name=f"{prefix}compliment [użytkownik=None]",
                         value="Daje komplement użytkownikowi [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ")
    help_embed.add_field(name=f"{prefix}diss [użytkownik=None]",
                         value="Dissuje użytkownikowi [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ")
    help_embed.add_field(name=f"{prefix}demote",
                         value="Demotywuje do życia (jakby samo życie nie wystarczało)")
    help_embed.add_field(name=f"{prefix}rdt [sub=memes] [limit=100]",
                         value="Wyświetla losowy obrazek z reddita na subreddicie [sub], losując spośród [limit] "
                               "najpopularniejszych obrazków")
    help_embed.add_field(name=f"{prefix}astro [znak]",
                         value="Wyświetla horoskop dla znaku [znak]")
    help_embed.add_field(name=f"{prefix}nameday",
                         value="Wyświetla imieniny dla obecnego dnia")
    help_embed.add_field(name=f"{prefix}wthr [miasto=Warszawa] [dni=0]",
                         value="Wyświetla prognozę pogody dla miasta [miasto], za [dni] dni")
    help_embed.add_field(name=f"{prefix}drink [nazwa drinka=None]",
                         value="Wyświetla losowy przepis na drinka, lub konkretny, jeśli podany")
    help_embed.add_field(name=f"{prefix}free [okres=current]",
                         value="Wyświetla listę darmowych gier z Epic Games Store, w okresie [okres]. Możliwe wartości: "
                               "current, upcoming")
    help_embed.add_field(name=f"{prefix}gif [fraza]",
                         value="Wyświetla losowy GIF z frazą [fraza]")
    help_embed.add_field(name=f"{prefix}topgif [fraza]",
                         value="Wyświetla najpopularniejszy GIF z frazą [fraza]")
    help_embed.add_field(name=f"{prefix}shipme",
                         value="Wyświetla ship dla Ciebie",
                         )
    help_embed.add_field(name=f"{prefix}shipstat",
                         value="Wyświetla użytkownika, z którym masz największą liczbę shipów",
                         )
    help_embed.add_field(name=f"{prefix}roll [dnd_dice_code=1d20]",
                         value="Rzuca kośćmi D&D w formacie [dnd_dice_code].\n"
                               "Przykłady: 1d20, d12, 2d6, 3d8+2, d6-2.\n"
                               "Domyślnie jest to kość 1d20",
                         )
    help_embed.add_field(name=f"{prefix}coin",
                         value="Rzuca monetą i wyświetla wynik (orzeł albo reszka)",
                         )
    help_embed.add_field(name=f"{prefix}sw [start/stop/reset]",
                         value="Uruchamia stoper, zatrzymuje go, lub resetuje",
                         )
    help_embed.add_field(name=f"{prefix}poll [treść]; [odp1]; [odp2]; ...",
                         value="Tworzy ankietę z podanych opcji. Treść i opcje muszą być oddzielone ;",
                         )
    help_embed.add_field(name=f"{prefix}essa [użytkownik=None]",
                         value="Wyświetla esse użytkownika [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                         )
    help_embed.add_field(name=f"{prefix}convert [metoda] [tekst]",
                         value="Konwertuje tekst [tekst] metodą [metoda]. Możliwe wartości: "
                               "s2b, b2s, s2h, h2s, s2b64, b642s",
                         )
    help_embed.add_field(name=f"{prefix}8ball [pytanie]",
                         value="Odpowiada na pytanie [pytanie] tak, jakby to była magiczna kula",
                         )
    help_embed.add_field(name=f"{prefix}story [opis]",
                         value="Tworzy historię za pomocą sztucznej inteligencji dla podanego opisu",
                         )
    help_embed.add_field(name=f"{prefix}pp [użytkownik=None]",
                         value="Wyświetla długość siurka użytkownika [użytkownik] jeśli podany, lub autorowi, "
                               "jeśli nie podany. Może przyjmować też zwykły tekst",
                         )
    help_embed.add_field(name=f"{prefix}uwu",
                         value="UwUalizuje wiadomość wyżej",
                         )
    help_embed.add_field(name=f"{prefix}ban [użytkownik]",
                         value="Banuje użytkownika [użytkownik]",
                         )
    help_embed.add_field(name=f"{prefix}money [akcja]",
                         value="Zarządzanie cebulionami. Możliwe wartości:\n"
                               "check - wyświetla stan konta\n"
                               "claim - odbiera dzienny bonus\n"
                               "add [ilość] - dodaje [ilość] cebulionów (tylko dla adminów)\n"
                               "remove [ilość] - usuwa [ilość] cebulionów (tylko dla adminów)\n"
                               "ranking - wyświetla ranking użytkowników",
                         )
    help_embed.add_field(name=f"{prefix}rr [akcja]",
                         value="Gra w ruletkę. Możliwe wartości:\n"
                               "set [czas] - ustawia czas obstawiania\n"
                               "start - rozpoczyna grę\n"
                               "bet [ilość] [typ] - obstawia [ilość] cebulionów na [typ]\n"
                               "prev - wyświetla poprzednie wyniki\n"
                               "img - wyświetla wygląd stołu do gry\n"
                               "help - wyświetla listę dostępnych typów zakładów",
                         )
    help_embed.add_field(name=f"{prefix}bday [akcja] <użytkownik> <data>",
                         value="Zarządzanie urodzinami. Możliwe wartości:\n"
                               "add <data> <użytkownik>- dodaje urodziny użytkownika <użytkownik> na dzień <data>\n"
                               "remove <użytkownik> - usuwa urodziny użytkownika <użytkownik>\n"
                               "get <użytkownik> - wyświetla urodziny użytkownika <użytkownik>\n"
                               "list - wyświetla listę urodzin\n"
                               "today - wyświetla listę urodzin na dziś\n"
                               "next - wyświetla najbliższe urodziny",
                         )
    help_embed.add_field(name=f"{prefix}gpt [wiadomość]",
                         value="Rozmowa ze sztuczną inteligencją (ChatGPT). "
                               "Można poprosić ją o pomoc, albo żeby coś zrobiła "
                               "(np. napisz streszczenie książki Ferdydurke)\n"
                               "Chat pamięta ostatnie 50 wiadomości.\n"
                               "Argumenty:\n"
                               "--clear - czyści historię rozmowy",
                         )
    help_embed.add_field(name=f"{prefix}f1",
                         value="Wyświetla następny wyścig Formuły 1",
                         )
    help_embed.add_field(name=f"{prefix}ryt",
                         value="Postuje losowy film z YouTube",
                         )
    help_embed.add_field(name=f"{prefix}lights [akcja]",
                         value="Przełączanie świateł w pokoju prezesa. Możliwe wartości:\n"
                               "main - przełącza główne światła\n"
                               "additional - przełącza dodatkowe światła\n"
                               "status - wyświetla status świateł\n"
                               "wakeup - budzi prezesa mrugając światałami\n"
                               "*** UWAGA *** panie Areczku, ta funkcja dostępna jest tylko dla zarządu",
                         )
    help_embed.add_field(name=f"{prefix}tts [tekst]",
                         value="Odtwarza tekst [tekst] jako mowę. Argumenty:\n"
                               "--join - dołącza do kanału głosowego\n"
                               "--leave - opuszcza kanał głosowy\n"
                               "Jeśli nie podano żadnego argumentu, bot dołączy do kanału głosowego, "
                               "odczyta tekst i opuści kanał głosowy",
                         )

    return help_embed.get_discord_embeds()
