import discord
from discord.ext import commands
from discord.ext import tasks


import os
import sys


import random
import json

import time
import datetime
import pytz
import mdbdict as mdb # <-- I MADE THIS
import pymongo

import asyncio

intents = discord.Intents.all()

intents.message_content = True
intents.presences = True
intents.members = True # redundant but it helps
intents.reactions = True
intents.voice_states = True

here = os.path.dirname(__file__)

path = os.path.dirname(os.path.realpath(__file__))
cogs = os.path.join(path, "cogs")
sys.path.append(os.path.join(path, "cogs"))

if len(sys.argv) == 1:
    os.environ["SHEPBOT_ENV"] = "testing"

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import cogs.settings as settings
if all([settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET, settings.PLAYLIST_LINK]):
    client_credentials_manager = SpotifyClientCredentials(client_id=settings.SPOTIFY_CLIENT_ID, client_secret=settings.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    playlist_URI = settings.PLAYLIST_LINK.split("/")[-1].split("?")[0]

    tracks = []
    for t in sp.playlist_tracks(playlist_URI)["items"]:
        data = {}
        data["name"] = t["track"]["name"]
        data["artist"] = t["track"]["artists"][0]["name"]
        data["length"] = t["track"]["duration_ms"] / 1000
        tracks.append(data)

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command("help")
        self.environment = ""
        self.db = mdb.MDict(settings.MONGO_URI)
        self.pymongodb = pymongo.MongoClient(settings.MONGO_URI)
        self.enabled = True

    def embed(self, title, color=None): # skeleton embed generator for all embeds outside of a cog
        if color is None:
            color = random.randint(0, 0xffffff)
        botembed = discord.Embed(title=title, color=color)

        if settings.PRIVATE_BOT:
            botembed.set_footer(text=self.response(0))
        botembed.timestamp = datetime.datetime.now()
        return botembed

    def current_time(self):
        return datetime.datetime.now(pytz.timezone("America/Los_Angeles"))

    async def on_ready(self):
        user = self.user

        
        if len(sys.argv) > 1:
            self.environment = "stable" # don't change these
        else:
            self.environment = "production" # don't change these

        print("-----")
        print(f"Logged in as: {user.name}#{user.discriminator}")
        print(f"ID: {user.id}")
        cloaded = 0
        for file in os.listdir(cogs):
            if file.endswith(".py"):
                #if file == "twitterfeed.py": continue
                name = file[:-3]
                with open(os.path.join(cogs, file), encoding="utf-8") as f:
                    try:
                        content = f.read()
                    except:
                        print(name)
                if "# DNI" not in content:  # "DNI": Do Not Import
                    await self.load_extension("cogs." + name, package=here)
                    cloaded += 1
        await self.load_extension("jishaku")
        cloaded += 1
        print(f"{cloaded} cogs loaded")
        print("-----") # if any errors are raised before this prints, fix them before restarting
        self.ready = True
        if all([settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET, settings.PLAYLIST_LINK]):
            self.update_status.start() # updates the status to shuffle through a spotify playlist

        with open(os.path.join(path, "assets", "starttime.txt"), "w") as f:
            f.write(str(time.time()))

    def response(self, resp_type): # base response function
        options = {
            0: "footer",
            1: "accepted",
            2: "error",
            3: "join",
            4: "leave",
            5: "praise"
        }
        with open(os.path.join(path, "assets", "responses.json")) as f:
            responses = json.loads(f.read())
        
        response = random.choice(responses[options[resp_type]])
        return response

    async def on_message(self, message):
        context = await self.get_context(message)
        if message.channel.id == settings.HALLOWEEN_CHANNEL:
            await self.process_commands(message)
            return
        if not self.enabled: 
            if not (message.author.id == settings.OWNER_ID and "toggle" in message.content):
                return
        if settings.PRIVATE_BOT:
            if message.guild:
                channel = self.get_channel(settings.MAIN_CHANNEL)
                if message.channel.id != channel.id and message.author.id != settings.OWNER_ID: 
                    return
            else: return
        await self.process_commands(message)

    @tasks.loop()
    async def update_status(self):
        random.shuffle(tracks)
        for t in tracks:
            await self.change_presence(activity=discord.Activity(
                name=f"{t['artist']} - {t['name']}", 
                type=discord.ActivityType.listening, 
                timestamps={"start": time.time() * 1000, "end": (time.time() + t["length"]) * 1000}
                
                ))
            await asyncio.sleep(t["length"])

        
p = (settings.PREFIX if len(sys.argv) != 1 else settings.PROD_PREFIX)
bot = Bot(command_prefix=p, activity=discord.Game(name=f"{p}help for help"), intents=intents)
bot.remove_command("help")

@bot.command()
async def quit(ctx):
    if ctx.author.id == settings.OWNER_ID:
        await ctx.send(embed=bot.embed("Shutting down..."))
        await bot.close()
        sys.exit()

@bot.command()
async def toggle(ctx):
    if ctx.author.id == settings.OWNER_ID:
        bot.enabled = not bot.enabled
        await bot.change_presence(status=discord.Status.offline if not bot.enabled else discord.Status.online)
        
        if not bot.enabled:
            await bot.update_status.cancel()
        else:
            await bot.update_status.start()

async def main():
    async with bot:
        if len(sys.argv) > 1:
            t = settings.TOKEN
            os.environ["SHEPBOT_ENV"] = "stable"
        else:
            t = settings.PROD_TOKEN
            os.environ["SHEPBOT_ENV"] = "testing"
        await bot.start(t)

if __name__ == "__main__":
    asyncio.run(main())