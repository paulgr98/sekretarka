import random

import asyncpraw
from discord.ext import commands

import config as cfg


async def get_subreddit_random_hot(subreddit, user, limit):
    async with asyncpraw.Reddit(client_id=cfg.CLIENT_ID,
                                client_secret=cfg.CLIENT_SECRET,
                                user_agent=cfg.USER_AGENT) as reddit:
        posts = []
        sub = await reddit.subreddit(subreddit)
        await sub.load()

        # check if subreddit is over 18 and the user doesn't have the mod permissions
        if sub.over18 and user.name != 'PanPajonk':
            raise commands.CommandError('O Ty zboczuszku! :3 Ten subreddit jest NSFW!')

        # if the limit is above 100, get the limit number of hot posts
        if limit > 50:
            hot = sub.hot(limit=limit)
        # if the limit is below 100, get 100 hot posts
        else:
            hot = sub.hot(limit=50)

        # get the posts with png, jpg, or gif extension
        async for submission in hot:
            if submission.url.endswith(('.jpg', '.png', '.gif')):
                posts.append({'author': submission.author, 'title': submission.title, 'url': submission.url})
        if len(posts) == 0:
            raise commands.CommandError('Nie ma takiego subreddita, albo nie ma na nim obrazków :(')

        # if there is more than limit number of hot posts, trim the list to limit
        if len(posts) > limit:
            posts = posts[:limit]

        return random.choice(posts)
