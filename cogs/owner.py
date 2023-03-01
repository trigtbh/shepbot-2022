from discord.ext import commands
import asyncio
import functions
import random
import settings
import io
import discord
from pytimeparse.timeparse import timeparse

def botembed(title):
    embed = functions.embed("Owner - " + title, color=0xffffff)
    return embed

def error(errormsg):
    embed = functions.error("Owner", errormsg)
    return embed

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stop = None

    async def confirmation(self, ctx):
        values = [c for c in "0123456789"]
        code = ""
        for _ in range(6):
            code += random.choice(values)
        def check(message):
            return message.content == code and message.channel == ctx.message.channel and message.author == ctx.message.author
        embed = botembed("Confirm")
        embed.description = "Are you sure you want to proceed? Type `{}` to proceed.".format(code)
        message = await ctx.send(embed=embed)
        try:
            _ = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return False, message
        else:
            return True, message

    async def cog_check(self, ctx):
        return ctx.author.id == settings.OWNER_ID 

    

    @commands.command()
    async def say(self, ctx, channel=None, *, message=None):
        if channel is None:
            embed = error("🚫 " + self.bot.response(2) + " you need to specify a channel.")
            return await ctx.send(embed=embed)
        if message is None and len(ctx.attachments) == 0:
            embed = error("🚫 " + self.bot.response(2) + " you need to provide a message to send.")
            return await ctx.send(embed=embed)
        
        try:
            test = int(channel)
        except:
            try:
                channel = await commands.TextChannelConverter().convert(ctx, channel)
            except Exception as e:
                embed = error("🚫 " + self.bot.response(2) + f" I couldn't find a channel named `{channel}`")
                return await ctx.send(embed=embed)
        else:
            channel = self.bot.get_channel(test)
            if not channel:
                embed = error("🚫 " + self.bot.response(2) + f" I couldn't find a channel with an ID of `{test}`")
                return await ctx.send(embed=embed)

        try:
            attachments = []
            for a in ctx.message.attachments:
                blank = io.BytesIO()
                await a.save(blank)
                new = discord.File(blank, filename=a.filename, spoiler=a.is_spoiler())
                attachments.append(new)
        except Exception as e:
            embed = error("🚫 " + self.bot.response(2) + f" I couldn't download attachments because of the following reason:\n```{str(e)}```")
            return await ctx.send(embed=embed)


        try:
            await channel.send(message, files=attachments)
        except Exception as e:
            embed = error("🚫 " + self.bot.response(2) + f" I couldn't send a message to `{channel.name}` because of the following reason:\n```{str(e)}```")
            return await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction("✅")

    @commands.Cog.listener()
    async def on_scheduled_event_user_add(self, event, user):
        if not self.bot.enabled: return
        owner = self.bot.get_user(settings.OWNER_ID)
        embed = botembed("User Added")
        embed.description = f"<@{user.id}> joined `{event.name}`."
        await owner.send(embed=embed)

    @commands.Cog.listener()
    async def on_scheduled_event_user_remove(self, event, user):
        if not self.bot.enabled: return
        owner = self.bot.get_user(settings.OWNER_ID)
        embed = botembed("User Left")
        embed.description = f"<@{user.id}> left `{event.name}`."
        await owner.send(embed=embed)

    @commands.Cog.listener()
    async def on_automod_action(self, execution):
        if not self.bot.enabled: return
        owner = self.bot.get_user(settings.OWNER_ID)
        embed = botembed("Automod Action")
        embed.description = f"Automod blocked a message by <@{execution.user_id}> in <#{execution.channel_id}>."
        embed.add_field(name="Message Content", value=execution.content, inline=False)
        embed.add_field(name="Matched Keyword", value=execution.matched_keyword, inline=False)
        await owner.send(embed=embed)

    @commands.command()
    async def ban(self, ctx, check=None):
        if check is None:
            embed = functions.error("Ban", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Ban", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        
        responses = ["no u", "L", "ratio", "ok", "bad", "1v1 me"]
        if settings.PRIVATE_BOT:
            responses = responses + settings.EXTRA_RESPONSES
        await ctx.message.reply(random.choice(responses))

    @commands.command()
    async def checkpoint(self, ctx, time="1h"):
        if not self.stop:
            duration = timeparse(time)
            if not duration: return
            self.stop = ctx.message.id
            await asyncio.sleep(duration)
            if self.stop == ctx.message.id: self.stop = None

    @commands.command()
    async def selfpurge(self, ctx, mod: str=None):
        if not self.stop: 
            return
        if mod == "all":
            conf, m = await self.confirmation(ctx)
            if not conf:
                return await m.delete()
        def check(m):
            if mod == "all":
                return m.id >= self.stop
            else:
                return m.author.id == ctx.author.id and m.id >= self.stop
        await ctx.channel.purge(check=check)
        self.stop = None

async def setup(bot):
    await bot.add_cog(Owner(bot))