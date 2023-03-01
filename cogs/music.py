
import asyncio
import discord
import re
import sys
import traceback
import wavelink
from discord.ext import commands
from typing import Union
import functions
from youtube_search import YoutubeSearch as ys
import random
import time
import settings
import os
import json

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def generate_code():
    chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    code = ""
    for _ in range(15):
        code = code + random.choice(chars)
    return code

def slice_n(lst, n):
    for i in range(0, len(lst), n): 
        yield lst[i:i + n] 

def botembed(title):
    embed = functions.embed("Music - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Music", errormsg)
    return embed
    
class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.bot.loop.create_task(self.connect_nodes())
        self.players = {}
        self.queues = {}
        self.playstates = {}
        self.test = {}
        self.p = None

    async def connect_nodes(self):
        #await self.bot.wait_until_ready()

        self.node = await wavelink.NodePool.create_node(bot=self.bot,
                                            host=settings.WL_HOST,
                                            port=settings.WL_PORT,
                                            password=settings.WL_PASSWORD,
                                            https=True)

        self.bot.node = self.node

        

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        if not self.bot.enabled: return
        if player.looping and reason != "STOPPED":
            await player.play(track)
            self.playstates[player.ctx.guild.id] = [time.time()]
        else:
            q = self.queues[player.guild.id]
            if not q.empty():
                track = q._queue.popleft()
                embed = botembed("Now Playing")
                embed.description = f"🎵 " + self.bot.response(3) + f" [{track.info['title']}]({track.info['uri']}) is now playing!"
                await player.ctx.send(embed=embed)
                self.playstates[player.ctx.guild.id] = [time.time()]
                player.current = track
                await player.play(track)
            else:
                self.playstates[player.ctx.guild.id] = []
                player.current = None

    async def cog_check(self, ctx):
        if not hasattr(ctx, "guild"): return False
        if not ctx.author.voice:
            embed = error("🚫 " + self.bot.response(2) + " you need to be connected to a voice channel to use this.")
            await ctx.send(embed=embed)
            return False
        if ctx.guild.id not in self.players.keys():
            if str(ctx.command) not in ["soundboard", "play"]:
                embed = error("🚫 " + self.bot.response(2) + " I'm not connected to a voice channel right now.")
                await ctx.send(embed=embed)
                return False
        else:
            player = self.players[ctx.guild.id]
            
            if player.channel.id != ctx.author.voice.channel.id:
                embed = error("🚫 " + self.bot.response(2) + " you need to be connected to the same voice channel as me to use this.")
                await ctx.send(embed=embed)
                return False
        return True

    

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack=None, silent=False):
        if ctx.guild.id not in self.players: # this cannot be put into a function or changed in any way
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            vc.ctx = ctx
            vc.looping = False
            await vc.set_volume(100)
            vc.channel = ctx.author.voice.channel
            self.players[ctx.guild.id] = vc
            self.queues[ctx.guild.id] = asyncio.Queue()
            self.playstates[ctx.guild.id] = []
        else:
            vc: wavelink.Player = ctx.voice_client
        
        queue = self.queues[ctx.guild.id]
        if queue.empty() and not vc.is_playing():
            self.playstates[ctx.guild.id] = [time.time()]
            vc.current = search
            await vc.play(search)
            if not silent:
                embed = botembed("Now Playing")
                embed.description = f"🎵 " + self.bot.response(3) + f" [{search.info['title']}]({search.info['uri']}) is now playing!"
                await ctx.send(embed=embed)
        else:
            await queue.put(search)
            if not silent:
                embed = botembed("Song Added")
                embed.description = ("📥 " + self.bot.response(1) +  f" `{search.info['title']}` has been added to the queue.")
                await ctx.send(embed=embed)
        
    @commands.command(aliases=['disconnect', 'dc', "dis", "leave"])
    async def stop(self, ctx: commands.Context):
        vc = self.players[ctx.guild.id]
        await vc.disconnect(force=True)
        embed = botembed("Disconnected")
        embed.description = "👋 " + self.bot.response(4) + f" I've disconnected from `{vc.channel.name}`."
        await ctx.send(embed=embed)
        del self.players[ctx.guild.id]
        del self.queues[ctx.guild.id]
        del self.playstates[ctx.guild.id]

    @commands.command(aliases=["s"])
    async def skip(self, ctx: commands.Context):
        vc = self.players[ctx.guild.id]
        await vc.stop()
        
    @commands.command()
    async def loop(self, ctx: commands.Context):
        vc = self.players[ctx.guild.id]
        vc.looping = not vc.looping
        embed = botembed("Loop Toggled")
        embed.description = "🔁 " + self.bot.response(1) +  " Looping has been `turned {}`.".format("on" if vc.looping else "off")
        return await ctx.send(embed=embed)

    @commands.command()
    async def move(self, ctx, frompos=None, topos=None):
        vc = self.players[ctx.guild.id]
        q = self.queues[ctx.guild.id]
        if frompos is None or topos is None:
            embed = error("🚫 " + self.bot.response(2) + " you must specify a position to move from and to.")
            return await ctx.send(embed=embed)
        try:
            frompos = int(frompos)
            topos = int(topos)
        except ValueError:
            embed = error("🚫 " + self.bot.response(2) + " you must specify a position to move from and to.")
            return await ctx.send(embed=embed)
        if frompos < 1 or frompos > len(q._queue):
            embed = error("🚫 " + self.bot.response(2) + " the position to move from is out of range.")
            return await ctx.send(embed=embed)
        if topos < 1 or topos > len(q._queue):
            embed = error("🚫 " + self.bot.response(2) + " the position to move to is out of range.")
            return await ctx.send(embed=embed)
        song = self.queues[ctx.guild.id]._queue[frompos - 1]
        self.queues[ctx.guild.id]._queue[frompos - 1] = self.queues[ctx.guild.id]._queue[topos - 1]
        self.queues[ctx.guild.id]._queue[topos - 1] = song
        
        embed = botembed("Song Moved")
        embed.description = "🔄 " + self.bot.response(1) +  f" [{song.info['title']}]({song.info['uri']}) has been moved from `#{frompos}` to `#{topos}` in the queue."
        return await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page=1):
        
        q = self.queues[ctx.guild.id]

        if q.empty():
            embed = error("🚫 " + self.bot.response(2) +  " there's nothing in the queue right now...")
            return await ctx.send(embed=embed)
        
        if not(str(page).isdigit()):
            embed = error("🚫 " + self.bot.response(2) +  " you need to pass a page number to view.")
            return await ctx.send(embed=embed)
        page = int(page)

        viewable = 5

        pages = int(len(q._queue) // viewable) + (1 if len(q._queue) % viewable > 0 else 0)

        page = min(max(page, 1), pages)
        start = (page-1) * viewable
        end = min(max(start + viewable, 1), len(q._queue))

        upcoming = list(q._queue)[start:end]

        desc = ""
        for i in range(len(upcoming)):
            desc = desc + f"\n**{start + i + 1}**: [{upcoming[i].info['title']}]({upcoming[i].info['uri']})" 

        embed = botembed(f"Queue (#{start + 1} - #{end})")

        embed.description = "🔢 " + self.bot.response(1) + f" Here's what's next...\n(Showing page {page} of {pages})\n" + desc

        await ctx.send(embed=embed)

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):
        vc = self.players[ctx.guild.id]
        if not vc.is_playing():
            embed = error("🚫 " + self.bot.response(2) +  " there's nothing playing right now...")
            return await ctx.send(embed=embed)

        temp = list(self.playstates[ctx.guild.id].copy())
        if len(temp) % 2 == 1:
            temp.append(time.time())

        chunked = list(slice_n(temp, 2))
        total = sum([x[1] - x[0] for x in chunked])
        
        length = time.gmtime(vc.current.info['length'] / 1000)
        if vc.current.info['length'] / 1000 >= 3600:
            fstring = "%H:%M:%S"
        else:
            fstring = "%M:%S"
        length_r = time.strftime(fstring, length)

        dt = time.gmtime(total)
        dt_r = time.strftime(fstring, dt)

        
        embed = botembed("Now Playing")
        embed.description = ("🔊 " + self.bot.response(1) + f" Currently, I'm playing [{vc.current.info['title']}]({vc.current.info['uri']})\n(`{dt_r}` / `{length_r}`).")
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, pos=None):
        q = self.queues[ctx.guild.id]
        if pos is None:
            embed = error("🚫 " + self.bot.response(2) +  " you must specify a position to remove.")
            return await ctx.send(embed=embed)
        try:
            pos = int(pos)
        except ValueError:
            embed = error("🚫 " + self.bot.response(2) +  " you must specify a position to remove.")
            return await ctx.send(embed=embed)
        if pos < 1 or pos > len(q._queue):
            embed = error("🚫 " + self.bot.response(2) +  " the position to remove is out of range.")
            return await ctx.send(embed=embed)
        song = q._queue[pos - 1]
        q._queue.remove(song)
        embed = botembed("Song Removed")
        embed.description = "📤 " + self.bot.response(1) + f" [{song.info['title']}]({song.info['uri']}) has been removed from the queue."
        return await ctx.send(embed=embed)

    @commands.command()
    async def pause(self, ctx):
        player = self.players[ctx.guild.id]
        if not player.is_playing:
            embed = error("🚫 " + self.bot.response(2) +  " it looks like I'm not playing anything right now...")
            return await ctx.send(embed=embed)

        embed = botembed("Paused")
        await player.set_pause(True)
        self.playstates[ctx.guild.id].append(time.time())
        embed.description = "⏸️ " + self.bot.response(1) + " I've paused the current song."
        await ctx.send(embed=embed)
        

    @commands.command(aliases=["res"])
    async def resume(self, ctx):
        player = self.players[ctx.guild.id]
        if not player.is_paused:
            embed = error("🚫 " + self.bot.response(2) +  " it looks like I'm not paused right now...")
            return await ctx.send(embed=embed)

        await player.set_pause(False)
        self.playstates[ctx.guild.id].append(time.time())
        embed = botembed("Resumed")
        embed.description = "▶️ " + self.bot.response(1) + " I've resumed the current song."
        await ctx.send(embed=embed)

    @commands.command(aliases=["vol"])
    async def volume(self, ctx, vol=None):
        player = self.players[ctx.guild.id]
        if not vol:
            embed = botembed("Current volume")
            embed.description = "🔊 " + self.bot.response(3) + f" The volume is currently set to `{player.volume}%`."
            return await ctx.send(embed=embed)
        elif not(vol.isdigit()):
            embed = error("🚫 " + self.bot.response(2) + " you need to pass a volume setting between 0 and 500.")
            return await ctx.send(embed=embed)
        
        vol = int(vol)
        vol = max(min(vol, 500), 0)
        await player.set_volume(vol)
        
        await player.set_volume(vol)
        embed = botembed("Volume Set")
        embed.description = "🔊 " + self.bot.response(1) + f" I set the volume to `{vol}%`."
        await ctx.send(embed=embed)

    @commands.command(aliases=["sb"])
    async def soundboard(self, ctx, query=None):
        with open(os.path.join(path, "assets", "soundboard.json")) as f:
            board = json.loads(f.read())

        if not query:
            embed = error("🚫 " + self.bot.response(2) +  " you need to specify a sound to play.\nThe current available sounds are:\n`" + "  ".join(sorted(board.keys())) + "`")
            return await ctx.send(embed=embed)
        
        query = query.lower().strip()

        if query not in board.keys():
            embed = error("🚫 " + self.bot.response(2) +  f" I couldn't find a sound named `{query}`.")
            return await ctx.send(embed=embed)

        if ctx.guild.id in self.players.keys():
            player = self.players[ctx.guild.id]
            if player:
                
                if not self.queues[ctx.guild.id].empty() or player.is_playing():
                    embed = error("🚫 " + self.bot.response(2) +  f" the soundboard cannot be used while music is playing or queued.")
                    return await ctx.send(embed=embed)
            
        await ctx.message.add_reaction("🎶")

        await ctx.invoke(self.play, search=list(await self.node.get_tracks(query=board[query], cls=wavelink.Track))[0], silent=True)




async def setup(bot):
    await bot.add_cog(Music(bot))