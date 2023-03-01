# DNI

import discord
from discord.ext import commands
import tweepy
import requests
import json
import settings
import asyncio

from tweepy.asynchronous import AsyncStreamingClient

class StreamClient(AsyncStreamingClient):
    async def on_tweet(self, tweet):
        headers = {"Authorization": "Bearer " + settings.BEARER_TOKEN}
        data = json.loads(requests.get("https://api.twitter.com/2/tweets/" + str(tweet.id) + "?user.fields=profile_image_url,name,username&tweet.fields=author_id", headers=headers).text)
        userdata = json.loads(requests.get("https://api.twitter.com/2/users/" + str(data["data"]["author_id"]) + "?user.fields=profile_image_url,name,username", headers=headers).text)["data"]
        payload = {"username": userdata["name"], "content": tweet.text + f"\n[View tweet](https://twitter.com/{userdata['username']}/statuses/{tweet.id})", "avatar_url": userdata["profile_image_url"]}
        requests.post(settings.WEBHOOK_URL, data=payload)

    async def on_errors(self, errors):
        print(f"Received error code {errors}")
        self.disconnect()
        return False

class TwitterFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_load(self):
        await self.bot.wait_until_ready()
        feed = StreamClient(settings.BEARER_TOKEN, wait_on_rate_limit=True)
        rules = await feed.get_rules()
        await feed.disconnect()
        return
        rules = rules.data
        if rules:
            await feed.delete_rules(rules)
        await feed.add_rules(tweepy.StreamRule("from:ShepGoesBlep"))
        self.bot.loop.create_task(feed.filter())
        await super().cog_load()

async def setup(bot):
    await bot.add_cog(TwitterFeed(bot))