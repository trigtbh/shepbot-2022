from datetime import datetime
from discord.ext import commands
import discord
import functions
import random
import settings
import asyncio
import time
from discord.ext import tasks
import os
import re
import unidecode
from textblob import TextBlob

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# to anyone that sees this in the future
# if you can find a better way to write all the repeated code for the commands 
# while still maintaining the same functionality
# you have all permission necessary to do so

def error(errormsg):
    embed = functions.error("Social", errormsg)
    return embed

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.address = ["sleepyheads", "everyone", "furros"]
        
        if settings.PRIVATE_BOT:
            c = self.bot.get_channel(settings.MAIN_CHANNEL)
            guild = c.guild
            self.server_owner = guild.owner.id
        
        

        self.check_online.start()
        self.goodnight.start()
        self.goodmorning.start()
        self.nicemessage.start()
        self.idkwhattocallthis.start()

    async def cog_before_invoke(self, ctx: commands.Context):
        if ctx.author.id == settings.OWNER_ID:
            return ctx.command.reset_cooldown(ctx)


    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if not self.bot.enabled: return
        if settings.PRIVATE_BOT and settings.EXTRA_ANNOYING:
            if before.id == self.server_owner:
                now = time.localtime()
                h = now.tm_hour
                if h > 21 or h < 6:
                    if before.status == discord.Status.offline and after.status != discord.Status.offline:
                        c = self.bot.get_channel(settings.MAIN_CHANNEL)
                        await c.send(f"<@{before.id}> go to sleep")

    @tasks.loop()
    async def goodnight(self, *args):
        if settings.PRIVATE_BOT:
            now = time.gmtime()
            h, m, s = now.tm_hour, now.tm_min, now.tm_sec
            totals = (h * 3600) + (m * 60) + s
            targets = 2 * 3600 + random.randint(-600, 600)
            

            distance = targets - totals
            if distance < 0:
                distance += (24 * 3600)
            elif distance == 0:
                return
            await asyncio.sleep(distance)

            channel = self.bot.get_channel(696764347770470403)
            
            message = random.choice(["Buenas noches", "Good night", "Go to sleep,", "Sleep tight"]) + " " + random.choice(self.address)

            await channel.send(message)
            await asyncio.sleep(60 * 20)

    @tasks.loop()
    async def idkwhattocallthis(self, *args):
        if settings.PRIVATE_BOT:
            now = time.gmtime()
            h, m, s = now.tm_hour, now.tm_min, now.tm_sec
            totals = (h * 3600) + (m * 60) + s
            targets = 16 * 3600 + random.randint(-600, 600)
            

            distance = targets - totals
            if distance < 0:
                distance += (24 * 3600)
            elif distance == 0:
                return
            await asyncio.sleep(distance)

            channel = self.bot.get_channel(696764347770470403)
            
            message = "Daily reminder that <@619684718505492510> is pretty epic" 

            #await channel.send(message)
            await asyncio.sleep(60 * 20) 

    @tasks.loop()
    async def goodmorning(self, *args):
        if settings.PRIVATE_BOT:
            now = time.gmtime()
            h, m, s = now.tm_hour, now.tm_min, now.tm_sec
            totals = (h * 3600) + (m * 60) + s
            targets = 12 * 3600 + random.randint(-600, 600)
            

            distance = targets - totals
            if distance < 0:
                distance += (24 * 3600)
            elif distance == 0:
                return
            await asyncio.sleep(distance)

            channel = self.bot.get_channel(696764347770470403)
            
            message = random.choice(["Buenos días", "Good morning", "Rise and shine", "Wake up"]) + " " + random.choice(self.address)

            if datetime.now().weekday() == 0:
                await channel.send(message, file=discord.File(os.path.join(base, "assets", "monday.mp4")))
            else:
                await channel.send(message)
            await asyncio.sleep(60 * 20)
            

    @tasks.loop()
    async def check_online(self, *args):
        if settings.PRIVATE_BOT and settings.EXTRA_ANNOYING:
            now = time.localtime()
            h, m, s = now.tm_hour, now.tm_min, now.tm_sec
            totals = (h * 3600) + (m * 60) + s
            targets = 21 * 3600
            

            distance = targets - totals
            if distance < 0:
                distance += (24 * 3600)
            elif distance == 0:
                return
            await asyncio.sleep(distance)
            c = self.bot.get_channel(settings.MAIN_CHANNEL)
            guild = c.guild
            
            m = guild.get_member(self.server_owner)
            if m.status != discord.Status.offline:
                await c.send(f"<@{m.id}> go to sleep")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.enabled: return
        context = await self.bot.get_context(message)
        if context.valid or message.author.bot: return 
        if message.author.bot: return
        if self.bot.user in message.mentions:
            if message.author.id == self.bot.user.id: return
            if message.author.id == settings.OWNER_ID and "how cute is" in message.content:
                return await message.channel.send("```Traceback (most recent call last):\n  File \"/app/cogs/social.py\", line 160 in on_message\n    self.bot.db[\"cuteness\"][hash(a)] = self.get_cuteness(a)\n  File \"/app/cogs/dbhelper.py\", line 124 in __add__\n    raise ValueError('value for \"' + column + '\" cannot be less than 0')\nValueError: value for \"cuteness\" cannot be less than 0```")
            if 696772352758775969 in [r.id for r in message.author.roles]:
                return
            #random.seed(message.author.id)
            lat = round(random.random() * 1000 % 180, 4)
            lon = round(random.random() * 1000 % 360, 4)
            
            if lat > 90:
                slat = str(180 - lat) + "°S"
            else:
                slat = str(lat) + "°N"

            if lon > 180:
                slon = str(360 - lon) + "°E"
            else:
                slon = str(lon) + "°W"

            #random.seed(message.author.id)
            responses = ["No u", "L", "Ratio", "Ok", "Bad", f"/ban <@{message.author.id}>", "1v1 me", f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)} :)", "Cringe", "Don't care", "Didn't ask", f"{slat}, {slon} :)"]
            if random.randint(1, 1000) == 1:
                return await message.reply(open(os.path.join(base, "assets", "wtf.txt"), encoding="utf-8").read())
            if settings.PRIVATE_BOT:
                responses = responses + settings.EXTRA_RESPONSES
            await message.reply(random.choice(responses))
        else:
            if message.author.id == self.bot.user.id: return
            if message.channel.id == 940024962339717173: return
            if 696772352758775969 in [r.id for r in message.author.roles]:
                return
            c = message.content.lower()
            owner = self.bot.get_user(settings.OWNER_ID)
            if "cheese" in c or "sergal" in c:
                await message.reply("Merp")
            elif "dog" in c:
                await message.reply("DOG")
            elif "toaster" in c or "proto" in c:
                await message.reply(random.choice(["Beep", "🍞", "Beep boop"]))
            elif "owo" in c or "uwu" in unidecode.unidecode(c):
                await message.reply(random.choice(["UwU", "OwO"])) # uwu is the best
                # funnily enough, copilot suggested the comment 
                # so it's staying
            elif "cute" in c:
                await message.reply("You're cute")
            elif "ball" in c or ":tennis:" in c:
                await message.reply(random.choice(["BALL", ":tennis:"]))
            elif "corn" in c:
                await message.reply("🌽")

            #elif "rawr" in c:
            #    await message.reply("X3 *nuzzles~* \*pounces on you\* UwU u so warm :3") # kill me please
            
            elif re.match(r"[Gg][(Rr)]{2,}", c):
                await message.reply("G" + "R" * random.randint(2, 10))
            elif re.match(r"[Aa]+[Hh]*[Ww]+[Oo][Oo]", c): # for some reason [Oo]{2,} doesn't work
                await message.reply("Aw" + "o" * random.randint(2, 10))
            #elif re.match(r"[Aa]([Ww]){2,}", c):
            #    await message.reply("Ok bottom") 
            #if "⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️🅱️🅰️" in c:
            #    await message.author.ban()
            
    @tasks.loop()
    async def nicemessage(self, *args):
        if settings.PRIVATE_BOT:
            now = time.gmtime()
            h, m, s = now.tm_hour, now.tm_min, now.tm_sec
            totals = (h * 3600) + (m * 60) + s
            targets = 19 * 3600 + random.randint(-3600 * 2, 3600)
            

            distance = targets - totals
            if distance < 0:
                distance += (24 * 3600)
            elif distance == 0:
                return
            await asyncio.sleep(distance)

            channel = self.bot.get_channel(696764347770470403)
            
            #message = "Daily reminder to drink water, go outside, and do what makes you happy :)"
            message = "Daily reminder that <@619684718505492510> is epic"
            # replace with something nice

            #await channel.send(message)
            await asyncio.sleep(3600 * 3) 
            

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def slap(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Slap", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Slap", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Slap", color=0xeb7d34)
        embed.description = f"Ouch! <@{ctx.author.id}> slapped <@{member.id}>!"

        gifs = [
            "https://c.tenor.com/EzwsHlQgUo0AAAAC/slap-in-the-face-angry.gif",
            "https://c.tenor.com/ImQ3_wc8sF0AAAAM/ru-paul-slap.gif",
            "https://c.tenor.com/yJmrNruFNtEAAAAC/slap.gif",
            "https://c.tenor.com/R-fs21xH13QAAAAM/slap-kassandra-lee.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def kiss(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Kiss", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Kiss", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Kiss", color=0xeb7d34)
        embed.description = f"Awww, <@{ctx.author.id}> kissed <@{member.id}>!"

        gifs = [
            "https://c.tenor.com/gUiu1zyxfzYAAAAi/bear-kiss-bear-kisses.gif",
            "https://c.tenor.com/zFzhOAJ8rqwAAAAC/love.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)
        
    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def punch(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Punch", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Punch", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Punch", color=0xeb7d34)
        embed.description = f"Ouch! <@{ctx.author.id}> punched <@{member.id}>!"

        gifs = [
            "https://c.tenor.com/5iVv64OjO28AAAAC/milk-and-mocha-bear-couple.gif",
            "https://c.tenor.com/UAG36LOiVDwAAAAC/milk-and-mocha-happy.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def hug(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Hug", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Hug", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Hug", color=0xeb7d34)
        embed.description = f"Awww, <@{ctx.author.id}> hugged <@{member.id}>!"

        gifs = [
            "https://c.tenor.com/OXCV_qL-V60AAAAM/mochi-peachcat-mochi.gif",
            "https://c.tenor.com/jU9c9w82GKAAAAAC/love.gif",
            "https://c.tenor.com/ZzorehuOxt8AAAAM/hug-cats.gif",
            "https://c.tenor.com/sSbr1al2-KQAAAAC/so-cute.gif",
            "https://c.tenor.com/5Xdf60Rv1a4AAAAC/milk-mocha.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def kill(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Kill", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Kill", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        
        embed = functions.embed("Kill", color=0xeb7d34)
        embed.description = f"{random.choice(['lmao', 'rip', 'L bozo'])} <@{member.id}> got killed by <@{ctx.author.id}>"
        embed.set_image(url="https://cdn.discordapp.com/emojis/864697428744339515.webp?size=512&quality=lossless")
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    @commands.has_permissions(administrator=True) # if you want to un-remove this then just comment this line out
    async def ship(self, ctx, user=None, *, other=None):
        if user is None:
            embed = functions.error("Ship", "🚫 " + self.bot.response(2) + " you need to specify a user.")
            return await ctx.send(embed=embed)
        if other is None:
            embed = functions.error("Ship", "🚫 " + self.bot.response(2) + f" you need to specify something/someone to ship the user with.")
            return await ctx.send(embed=embed)
        
        try:
            member = await commands.MemberConverter().convert(ctx, user)
        except Exception as e:
            embed = functions.error("Ship", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{user}`.")
            return await ctx.send(embed=embed)

        try:
            other = await commands.MemberConverter().convert(ctx, other)
        except Exception as e:
            pass

        val = abs(hash("".join(sorted(str(member) + str(other)))))
        if random.random() < 0.1:
            val = round(val / 10, 3) # less than 10%
        if random.random() == 1.0:
            val = 100.000

        compat = round(val / (10 ** len(str(val))) * 100, 3)
        ratings = ["Never happening", "Awful", "Horrible", "Bad", "Not great", "Decent", "Fine", "Good", "Great", "Perfect"]
        embed = functions.embed("Ship", color=0xeb7d34)
        if isinstance(other, discord.Member):
            other = "<@" + str(other.id) + ">"
        embed.description = f"**<@{member.id}> + {other}**\n\nCompatibility: `{compat}%`\nRating: **{ratings[int(compat // 10)]}**"
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def poke(self, ctx, check: str = None):
        if check is None:
            embed = functions.error("Poke", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Poke", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Poke", color=0xeb7d34)
        embed.description = f"Ouch! <@{ctx.author.id}> poked <@{member.id}>!"

        gifs = [
            "https://c.tenor.com/qkvoAoV4w3wAAAAC/poke-cute-bear.gif",
            "https://c.tenor.com/KyPxfr4AVFcAAAAC/poke.gif",
            "https://c.tenor.com/9bPsSkaKgVsAAAAC/poke-boop.gif",
            "https://c.tenor.com/my_TpYpdQX0AAAAC/yeah-im-hungry-milk-and-mocha.gif"

        ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def boop(self, ctx, check: str=None):
        if check is None:
            embed = functions.error("Boop", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Boop", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
            
        embed = functions.embed("Boop", color=0xeb7d34)
        embed.description = f"Awww, <@{ctx.author.id}> booped <@{member.id}>!"
        gifs = [
            "https://c.tenor.com/MQ5Kdsh3zKMAAAAM/boop-dog-high-quality.gif",
            "https://c.tenor.com/WM6gQWWPvIcAAAAC/boop-wolf.gif",
            "https://c.tenor.com/le048t71RHwAAAAC/boop.gif",
            
        ]

        if member.id == 424991711564136448 and ctx.author.id != 355144999060373516:
            gifs = [
                "https://c.tenor.com/XRIjYboNkT4AAAAC/protogen-protogen-boop.gif"
            ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def pat(self, ctx, check: str=None):
        if check is None:
            embed = functions.error("Pat", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Pat", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Pat", color=0xeb7d34)
        embed.description = f"Awww, <@{ctx.author.id}> patted <@{member.id}> on the head!"
        gifs = [
            "https://c.tenor.com/GU0IIlOZUQ0AAAAC/pat-pat.gif",
            "https://c.tenor.com/5MGEjar4AHcAAAAC/seal-hibo.gif",
            "https://c.tenor.com/qjHkX9X0FOQAAAAC/milk-and-mocha-pat.gif",
            "https://c.tenor.com/AZ1mlSh-fT8AAAAi/pat-duck.gif",
            "https://c.tenor.com/BWXvOyKVWU4AAAAi/potato-pat.gif"

        ]
        if member.id == 424991711564136448 and ctx.author.id != 355144999060373516:
            gifs = [
                "https://c.tenor.com/-jJlxJOR2yIAAAAC/moose-protogen.gif"
            ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def bonk(self, ctx, check: str=None):
        if check is None:
            embed = functions.error("Bonk", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Bonk", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        embed = functions.embed("Bonk", color=0xeb7d34)
        embed.description = f"Ouch! <@{ctx.author.id}> bonked <@{member.id}>!"
        gifs = [
            "https://c.tenor.com/DMWqIb2Rdp4AAAAj/bonk-cheems.gif",
            "https://c.tenor.com/WQE5mJQSRRsAAAAj/bonk-hit.gif",
            "https://c.tenor.com/5YrUft9OXfUAAAAM/bonk-doge.gif",
            "https://c.tenor.com/Tg9jEwKCZVoAAAAd/bonk-mega-bonk.gif"
        ]
        if member.id == 424991711564136448 and ctx.author.id != 355144999060373516:
            gifs = [
                "https://c.tenor.com/k2Egl6BtjdoAAAAC/bonk-protogen.gif"
            ]

        embed.set_image(url=random.choice(gifs))
        return await ctx.send(embed=embed)

    # if you want to uncomment this then go ahead
    """@commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 10, commands.BucketType.user)
    @commands.command()
    async def cute(self, ctx, check: str=None):
        if check is None:
            embed = functions.error("Cute", "🚫 " + self.bot.response(2) + f" it looks like you need to specify a user.")
            return await ctx.send(embed=embed)
        try:
            member = await commands.MemberConverter().convert(ctx, check)
        except Exception as e:
            embed = functions.error("Cute", "🚫 " + self.bot.response(2) + f" I couldn't find a user named `{check}`.")
            return await ctx.send(embed=embed)
        random.seed(hash(member.avatar))
        embed = functions.embed("Cute", color=0xeb7d34)
        embed.description = f"Checking cuteness of <@{member.id}>..."
        if member.id == ctx.guild.owner.id:
            perc = "110.00"
        else:
            perc = str(random.randint(5000, 10000) / 100)
        embed.set_thumbnail(url=member.avatar)
        m = await ctx.send(embed=embed)
        await asyncio.sleep(3 + (random.randint(5, 15) / 10))
        embed.description = "<@" + str(member.id) + "> is **`" + perc + "%`** cute!"
        return await m.edit(embed=embed)"""

async def setup(bot):
    await bot.add_cog(Social(bot))