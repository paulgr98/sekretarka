import discord


def get_help_embed(prefix: str) -> list[discord.Embed]:
    embeds = []
    embed = discord.Embed(title="Pomoc 1/2", description="Lista komend", color=0x00ff00)
    embed.add_field(name=f"{prefix}ping",
                    value="Testuje połącznie",
                    inline=False)
    embed.add_field(name=f"{prefix}hi",
                    value="Wita się",
                    inline=False)
    embed.add_field(name=f"{prefix}purge [ilość=2]",
                    value="Usuwa [ilość] wiadomości wyżej. Domyślnie, bez podawania jawnie, ilość=2",
                    inline=False)
    embed.add_field(name=f"{prefix}undo [ilość=1]",
                    value="Usuwa [ilość] ostatnich wiadomości bota. Domyślnie, bez podawania jawnie, ilość=1",
                    inline=False)
    embed.add_field(name=f"{prefix}compliment [użytkownik=None]",
                    value="Daje komplement użytkownikowi [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                    inline=False)
    embed.add_field(name=f"{prefix}diss [użytkownik=None]",
                    value="Dissuje użytkownikowi [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                    inline=False)
    embed.add_field(name=f"{prefix}demote",
                    value="Demotywuje do życia (jakby samo życie nie wystarczało)",
                    inline=False)
    embed.add_field(name=f"{prefix}rdt [sub=memes] [limit=100]",
                    value="Wyświetla losowy obrazek z reddita na subreddicie [sub], losując spośród [limit] "
                          "najpopularniejszych obrazków",
                    inline=False)
    embed.add_field(name=f"{prefix}astro [znak]",
                    value="Wyświetla horoskop dla znaku [znak]",
                    inline=False)
    embed.add_field(name=f"{prefix}nameday",
                    value="Wyświetla imieniny dla obecnego dnia",
                    inline=False)
    embed.add_field(name=f"{prefix}wthr [miasto=Warszawa] [dni=0]",
                    value="Wyświetla prognozę pogody dla miasta [miasto], za [dni] dni",
                    inline=False)
    embed.add_field(name=f"{prefix}drink [nazwa drinka=None]",
                    value="Wyświetla losowy przepis na drinka, lub konkretny, jeśli podany",
                    inline=False)
    embed.add_field(name=f"{prefix}free [okres=current]",
                    value="Wyświetla listę darmowych gier z Epic Games Store, w okresie [okres]. Możliwe wartości: "
                          "current, upcoming",
                    inline=False)
    embed.add_field(name=f"{prefix}gif [fraza]",
                    value="Wyświetla losowy GIF z frazą [fraza]",
                    inline=False)
    embed.add_field(name=f"{prefix}topgif [fraza]",
                    value="Wyświetla najpopularniejszy GIF z frazą [fraza]",
                    inline=False)

    embed2 = discord.Embed(title="Pomoc 2/2", description="Lista komend", color=0x00ff00)
    embed2.add_field(name=f"{prefix}shipme",
                     value="Wyświetla ship dla Ciebie",
                     inline=False)
    embed2.add_field(name=f"{prefix}shipstat",
                     value="Wyświetla użytkownika, z którym masz największą liczbę shipów",
                     inline=False)
    embed2.add_field(name=f"{prefix}roll [minimum=1] [maximum=6]",
                     value="Wyświetla losową liczbę między [minimum] a [maximum]",
                     inline=False)
    embed2.add_field(name=f"{prefix}coin",
                     value="Rzuca monetą i wyświetla wynik (orzeł albo reszka)",
                     inline=False)
    embed2.add_field(name=f"{prefix}sw [start/stop/reset]",
                     value="Uruchamia stoper, zatrzymuje go, lub resetuje",
                     inline=False)
    embed2.add_field(name=f"{prefix}poll [treść]; [odp1]; [odp2]; ...",
                     value="Tworzy ankietę z podanych opcji. Treść i opcje muszą być oddzielone ;",
                     inline=False)
    embed2.add_field(name=f"{prefix}essa [użytkownik=None]",
                     value="Wyświetla esse użytkownika [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                     inline=False)
    embed2.add_field(name=f"{prefix}convert [metoda] [tekst]",
                     value="Konwertuje tekst [tekst] metodą [metoda]. Możliwe wartości: "
                           "s2b, b2s, s2h, h2s, s2b64, b642s",
                     inline=False)
    embed2.add_field(name=f"{prefix}8ball [pytanie]",
                     value="Odpowiada na pytanie [pytanie] tak, jakby to była magiczna kula",
                     inline=False)
    embed2.add_field(name=f"{prefix}story [opis]",
                     value="Tworzy historię za pomocą sztucznej inteligencji dla podanego opisu",
                     inline=False)
    embed2.add_field(name=f"{prefix}pp [użytkownik=None]",
                     value="Wyświetla długość siurka użytkownika [użytkownik] jeśli podany, lub autorowi, "
                           "jeśli nie podany. Może przyjmować też zwykły tekst",
                     inline=False)
    embed2.add_field(name=f"{prefix}story [słowo_kluczowe]",
                     value="Tworzy historię dla podanego słowa kluczowego [słowo_kluczowe]",
                     inline=False)
    embed2.add_field(name=f"{prefix}uwu",
                     value="UwUalizuje wiadomość wyżej",
                     inline=False)
    embed2.add_field(name=f"{prefix}ban [użytkownik]",
                     value="Banuje użytkownika [użytkownik]",
                     inline=False)
    embed2.add_field(name=f"{prefix}money [akcja]",
                     value="Zarządzanie cebulionami. Możliwe wartości:\n"
                           "check - wyświetla stan konta\n"
                           "claim - odbiera dzienny bonus\n"
                           "add [ilość] - dodaje [ilość] cebulionów (tylko dla adminów)\n"
                           "remove [ilość] - usuwa [ilość] cebulionów (tylko dla adminów)"
                           "ranking - wyświetla ranking użytkowników",
                     inline=False)
    embed2.add_field(name=f"{prefix}rr [akcja]",
                     value="Gra w ruletkę. Możliwe wartości:\n"
                           "set [czas] - ustawia czas obstawiania\n"
                           "start - rozpoczyna grę\n"
                           "bet [ilość] [typ] - obstawia [ilość] cebulionów na [typ]"
                           "prev - wyświetla poprzednie wyniki"
                           "img - wyświetla wygląd stołu do gry"
                           "help - wyświetla listę dostępnych typów zakładów",
                     inline=False)
    embed2.add_field(name=f"{prefix}bday [akcja] <użytkownik> <data>",
                     value="Zarządzanie urodzinami. Możliwe wartości:\n"
                           "add <data> <użytkownik>- dodaje urodziny użytkownika <użytkownik> na dzień <data>\n"
                           "remove <użytkownik> - usuwa urodziny użytkownika <użytkownik>\n"
                           "get <użytkownik> - wyświetla urodziny użytkownika <użytkownik>\n"
                           "list - wyświetla listę urodzin"
                           "today - wyświetla listę urodzin na dziś"
                           "next - wyświetla najbliższe urodziny",
                     inline=False)
    embed2.add_field(name=f"{prefix}gpt [wiadomość]",
                     value="Rozmowa ze sztuczną inteligencją (ChatGPT). "
                           "Można poprosić ją o pomoc, albo żeby coś zrobiła "
                           "(np. napisz streszczenie książki Ferdydurke)",
                     inline=False)

    embeds.append(embed)
    embeds.append(embed2)
    return embeds
