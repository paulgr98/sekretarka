from components import news_feed
import discord


async def get_news_embeds(number: int = 5) -> list[discord.Embed]:
    tvn24 = news_feed.Tvn24Feed()
    tvn24.set_src_to_importants()
    news = tvn24.get_news()
    embeds = []
    for event in news[:number]:
        embed = discord.Embed(title=event['title'], url=event['link'])
        embeds.append(embed)

    return embeds
