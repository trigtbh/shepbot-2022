import discord
from discord.ext import commands
import random
import functions
import asyncio
import math
import mongohelper as mh
import time
import os


def botembed(title):
    embed = functions.embed("Leveling - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Leveling", errormsg)
    return embed


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.leveldb = self.bot.pymongodb["MainDatabase"]["leveling"]
        

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.enabled: return
        if os.environ["SHEPBOT_ENV"] == "testing": return
        context = await self.bot.get_context(message)
        if context.valid: return
        if message.author.bot: return

        blacklist_servers = {
            982488812208930866
        }

        blacklist_channels = {
            696766682546307193,
            766707126755917915,
            982671777085931540,
            1011345441352335470,
            982026809501687919,
            699275401746186370
        }
        blacklist_categories = {
            1006304050301644970,
            696764347770470402
        }

        if isinstance(message.channel, discord.channel.DMChannel): return
        
        if message.guild.id in blacklist_servers: return
        if message.channel.id in blacklist_channels: return
        if message.channel.category_id in blacklist_categories: return
        
        author = message.author
        if not mh.find(self.leveldb, author.id):
            mh.add(self.leveldb, {"_id": author.id, "level": 0, "xp": 0, "cooldown": time.time() - 61, "total": 0})
        data = mh.find(self.leveldb, author.id)
        level = data["level"]
        if level >= 100: return
        if time.time() - data["cooldown"] >= 60:
            new = random.randint(15, 25)
            xp = data["xp"] + new
            total = data["total"] + new
            if xp >= (5 * (level ** 2) + (50 * level) + 100):
                xp -= (5 * (level ** 2) + (50 * level) + 100)
                level += 1
                embed = botembed("Level Up!")
                desc = "⏫ You leveled up! " + self.bot.response(5) + " You are now level " + str(level) + "."
                if level == 100:
                    desc = desc + "\nYou have hit the maximum level! Congratulations!"
                embed.description = desc
                channel = self.bot.get_channel(982671777085931540)
                await channel.send("<@" + str(message.author.id) + ">", embed=embed)
            mh.update(self.leveldb, author.id, {"xp": xp, "level": level, "cooldown": time.time(), "total": total})

    @commands.command()
    async def rank(self, ctx, target: str=None):
        embed = botembed("Current Rank")
        data = self.leveldb
        
        defaulted = False
        if target is None:
            target = ctx.author
            defaulted = True
        else:
            try:
                target = await commands.MemberConverter().convert(ctx, target)
            except Exception as e:
                embed = functions.error("Rank", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{target}`.")
                return await ctx.send(embed=embed)

        if not defaulted:
            if target.bot:
                embed = functions.error("Rank", "🚫 " + self.bot.response(2) + " bots don't have ranks.")
                return await ctx.send(embed=embed)

        if not defaulted:
            user = mh.find(data, target.id)
            u = target.id
        else:
            user = mh.find(data, ctx.author.id)
            u = ctx.author.id
        if not user:
            if defaulted:
                return await ctx.send(embed=error("🚫 " + self.bot.response(2) + " it looks like they're not on the leaderboard yet."))
            else:
                return await ctx.send(embed=error("🚫 " + self.bot.response(2) + " it looks like you're not on the leaderboard yet. Send messages to gain XP and level up!"))
    
        
        sortedranks = [uid["_id"] for uid in sorted([c for c in data.find()], key=lambda x: x["total"])][::-1]
        level = "🔢 Level: **" + str(user["level"]) + "**"
        xp = "✨ XP: **" + str(user["xp"]) + "/" + str(5 * (user["level"] ** 2) + (50 * user["level"]) + 100) + "**"
        index = sortedranks.index(u)
        rankemoji = {0: "🥇", 1: "🥈", 2: "🥉"}.get(index, "#️⃣")
        rank = rankemoji + " Rank: **#" + str(index + 1) + "/" + str(len([u for u in ctx.guild.members if not u.bot])) + "**"
        embed.description = "🙋 Rank for: **<@{}>**".format(u) + "\n" + level + "\n" + xp + "\n" + rank
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx, page=None):
        embed = botembed("Leaderboard")
        data = self.leveldb
        if not page:
            page = 1
        else:
            try:
                page = int(page)
            except:
                return await ctx.send(embed=error("🚫 " + self.bot.response(2) + " that's not a valid page number."))
        if page < 1:
            return await ctx.send(embed=error("🚫 " + self.bot.response(2) + " that's not a valid page number."))
        sortedranks = [uid["_id"] for uid in sorted([c for c in data.find()], key=lambda x: x["total"])][::-1]
        if page > math.ceil(len(sortedranks) / 10):
            return await ctx.send(embed=error("🚫 " + self.bot.response(2) + " that's not a valid page number."))
        embed.description = "🙋 Leaderboard for: **" + ctx.guild.name + "**\nPage `" + str(page) + "/" + str(math.ceil(len(sortedranks) / 10)) + "`\n\n"
        for i in range(10):
            try:
                user = sortedranks[(page - 1) * 10 + i]
                user = mh.find(data, user)
                if page == 1:
                    rankemoji = {0: "🥇 ", 1: "🥈 ", 2: "🥉 "}.get(i, "")
                    rank = rankemoji + "**#" + str((page - 1) * 10 + i + 1) + "**: <@" + str(user["_id"]) + "> - Level `" + str(user["level"]) + "`\n"
                    embed.description += rank
                else:
                    embed.description += "**#" + str((page - 1) * 10 + i + 1) + "**: <@" + str(user["_id"]) + "> - Level `" + str(user["level"]) + "`\n"
            except:
                break
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))