from discord.ext import commands
import functions
import random
import asyncio
import settings

def botembed(title):
    embed = functions.embed("Moderation - " + title, color=0x0575ed)
    return embed

def error(errormsg):
    embed = functions.error("Moderation", errormsg)
    return embed

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db["MainDatabase"]["raid"]

    async def cog_check(self, ctx):
        if ctx.author.id == 424991711564136448:
            return True
        if 696772352758775969 not in [role.id for role in ctx.author.roles]:
            embed = error("🚫 " + self.bot.response(2) + " you do not have permission to use this command.")
            await ctx.send(embed=embed)
            return False
        return True

    async def confirmation(self, ctx, message="Are you sure you want to proceed?"):
        values = [c for c in "0123456789"]
        code = ""
        for _ in range(6):
            code += random.choice(values)
        def check(message):
            return message.content == code and message.channel == ctx.message.channel and message.author == ctx.message.author
        embed = botembed("Confirm")
        embed.description = "**" + message + "**\nType `{}` to proceed.".format(code)
        message = await ctx.send(embed=embed)
        try:
            _ = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return False, message
        else:
            return True, message

    @commands.command()
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)
        embed = botembed("Purge")
        embed.description = "🗑️ " + self.bot.response(1) + f" {amount} message{'' if amount == 1 else 's'} have been deleted."
        await ctx.send(embed=embed, delete_after=5.0)

    @commands.command()
    async def raid(self, ctx):
        if len(self.db) == 0:
            self.bot.db["MainDatabase"]["raid"].append({"_id": settings.MAIN_CHANNEL})
            # step 1: disable new people from gaining access to the server automatically
            channel = self.bot.get_channel(settings.ROLES_CHANNEL)
            await channel.set_permissions(ctx.guild.default_role, view_channel=False)

            # step 2: send an announcement in the announcements channel
            channel = self.bot.get_channel(settings.ANNOUNCEMENTS_CHANNEL)
            embed = botembed("Raid Mode Enabled")
            embed.description = "Raid Mode has been enabled for the server by a staff member.\nThis will not affect your ability to use the server.\nHowever, if you leave and rejoin, you will not be able to gain access until Raid Mode has been lifted.\nIf new members are causing any trouble, DM a staff member.\nPlease be patient while the issue gets resolved."
            await channel.send("<@696776350127620218>", embed=embed)
        else:
            conf, m = await self.confirmation(ctx, message="Are you sure you want to disable Raid Mode?")
            if not conf:
                return await m.delete()
            
            # step 1: enable new people to gain access to the server automatically
            channel = self.bot.get_channel(settings.ROLES_CHANNEL)
            await channel.set_permissions(ctx.guild.default_role, view_channel=True)

            # step 2: send an announcement in the announcements channel
            channel = self.bot.get_channel(settings.ANNOUNCEMENTS_CHANNEL)
            embed = botembed("Raid Mode Disabled")
            embed.description = "Raid Mode has been disabled.\nThank you for your patience."
            await channel.send(embed=embed)

            embed = botembed("Raid Mode Disabled")
            embed.description = "Raid Mode disabled."
            await ctx.send(embed=embed)
            del self.bot.db["MainDatabase"]["raid"][0]

async def setup(bot):
    await bot.add_cog(Moderation(bot))