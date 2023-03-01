import discord
from discord.ext import commands, tasks

import functions
import settings 
import random
import asyncio
import mongohelper as mh
import os
import json
import math
import time
import traceback

def botembed(title):
    embed = functions.embed("Halloween - " + title, color=0xfc8c03)
    return embed

def error(errormsg):
    embed = functions.error("Halloween", errormsg)
    return embed

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Halloween(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queued = False
        with open(os.path.join(base, "assets", "halloween", "halloween_items.json")) as f:
            self.items = json.load(f)
        self.hdb = self.bot.pymongodb["MainDatabase"]["halloween"]
        self.images = [f for f in os.listdir(os.path.join(base, "assets", "halloween", "images")) if os.path.isfile(os.path.join(base, "assets", "halloween", "images", f))]
        self.raiseerror = True
        self.mtype = 0
        self.active = []
        self.required = []
        self.lookingfor = 0
        self.weights = [75, 20, 4, 1]
        self.first_announcement.start()
        self.last_announcement.start()

    @tasks.loop(count=1)
    async def first_announcement(self):
        future = 1664596800
        if future - time.time() < 0: return
        await asyncio.sleep(future - time.time())
        if not self.bot.enabled: return

        channel = self.bot.get_channel(766707126755917915)
        guild = channel.guild
        role = guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        await channel.set_permissions(role, overwrite=overwrite)
        

        embed = functions.embed("The Halloween Event has started!", color=0xfc8c03)
        embed.description = "The month of October is finally upon us! To celebrate, we're bringing back the month-long event of *trick-or-treating!*"
        embed.add_field(name="How does it work?", value="Head on over to <#766707126755917915> and wait for trick-or-treaters to arrive.\nWhen they do, they will ask for either a **trick** or a **treat**.\nRespond by using either `>trick` or `>treat`, respectively.\nThe first person to do so will be gifted a random item in return.", inline=False)
        embed.add_field(name="What do I do with these items?", value="What fun would there be without a bit of *competition*?\nThere are a total of 100 unique items that you can collect.\nDuring the event, a leaderboard will be made that displays the users in the server with the most unique items.\nAt the end of the event, the person at the top of the leaderboard will be declared the **Champion of Halloween** and receive the <@&766705680216096808> role.\nThis role, in addition to adding an orange color to your name, *will prominently display you at the very top of the server members list*.\nIf there is a tie, all tied members will receive the role.\n", inline=False)
        embed.add_field(name="How long does it go on for?", value="The event starts on <t:1664596800:f> and lasts until <t:1667275200:f>.", inline=False)
        embed.add_field(name="Anything else I should know?", value="- Some of the items may reference other things - try and see if you can spot them all!\n- Items might be randomly distributed throughout the month, so be on the lookout for surprise drops!\n- Going for all 100 items takes a *ton* of commitment - it might not even be physically possible. If you do somehow manage to pull it off, you will have every bit of my respect.\n\nGood luck, and remember to have fun! 🎃", inline=False)
        channel = self.bot.get_channel(761977812688175124)
        await channel.send("<@&761978417783636028>", embed=embed)

    @tasks.loop(count=1)
    async def last_announcement(self):
        future = 1667275200
        if future - time.time() < 0: return
        await asyncio.sleep(future - time.time())
        if not self.bot.enabled: return

        channel = self.bot.get_channel(766707126755917915)
        guild = channel.guild
        role = guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        await channel.set_permissions(role, overwrite=overwrite)


        embed = functions.embed("The Halloween Event has ended!", color=0xfc8c03)
        embed.description = "The Halloween Event has officially ended. Thank you to everyone who participated!\nHere are the top 10 users with the most unique items:"
        data = self.hdb.find()
        data = [d for d in data]
        data = sorted(data, key=lambda x: sum([bin(x[test])[1:].count("1") for test in x if test != "_id"]), reverse=True)
        for i, user in enumerate(data):
            if i == 10:
                break
            items = []
            for r in self.items:
                items += [self.items[r][i] for i in range(len(self.items[r])) if bin(user[r.lower()])[2:].rjust(len(self.items[r]), "0")[i] == "1"]
            embed.description += f"\n{i+1}. **<@{user['_id']}> - {len(items)} items**"
        

        if len(data) > 0:
            if len(data) > 1:
                if sum([bin(data[0][test])[1:].count("1") for test in data[0] if test != "_id"]) == sum([bin(data[1][test])[1:].count("1") for test in data[1] if test != "_id"]):
                    embed.description += "\n\nThere was a tie for first place, so the following users have been awarded the <@&766705680216096808> role:"
                    for i, user in enumerate(data):
                        if i == 0:
                            embed.description += f"\n- **<@{user['_id']}>**"
                            continue
                        if sum([bin(data[0][test])[1:].count("1") for test in data[0] if test != "_id"]) == sum([bin(data[i][test])[1:].count("1") for test in data[i] if test != "_id"]):
                            embed.description += f"\n- **<@{user['_id']}>**"
                        else:
                            break
                    embed.description += "\n\nCongratulations to all of the winners!\nYou are officially 2022's **Champions of Halloween**! 🎃"
                else:
                    embed.description += "\n\nCongratulations to <@!{}> for winning the event!\nYou are officially 2022's **Champion of Halloween**! 🎃".format(data[0]["_id"])
        channel = self.bot.get_channel(761977812688175124)
        await channel.send("<@&761978417783636028>", embed=embed)

    @commands.command()
    async def trick(self, ctx):
        if not(1664596800 <= time.time() <= 1667275200): return
        if not self.bot.enabled: return
        if self.raiseerror:
            await ctx.send(embed=error("🚫 " + self.bot.response(2) +  f" there's nobody to give a trick to..."))
            return

    @commands.command()
    async def treat(self, ctx):
        if not(1664596800 <= time.time() <= 1667275200): return
        if not self.bot.enabled: return
        if self.raiseerror:
            await ctx.send(embed=error("🚫 " + self.bot.response(2) +  f" there's nobody to give a treat to..."))
            return
        
    @commands.command()
    async def setrates(self, ctx, ratenum):
        if ctx.author.id != settings.OWNER_ID: return
        self.weights = [int(ratenum) for ratenum in ratenum.split(":")]
        embed = botembed("Rates set")
        embed.description = "Rates changed to:\n" + "\n".join([f"{list(self.items.keys())[i]}: {self.weights[i]}%" for i in range(len(self.items))])
        await ctx.send(embed=embed)

    def check(self, message):
        if message.channel.id == settings.HALLOWEEN_CHANNEL:
            c = message.content.strip().lower()
            if len(c) < 3: return None
            if self.lookingfor == 1:
                return c[0] == settings.PREFIX and c[1:] in {"trick", "treat"}
            else:
                if c[0] == settings.PREFIX and c[1:] in {"trick", "treat"}:
                    go = True
                    if len(self.active) > 0:
                        for m in self.active:
                            if m.author.id == message.author.id:
                                go = False
                                break
                    if go:
                        self.active.append(message)
                        if len(self.active) == 2 or c[1:] != ["trick", "treat"][self.mtype - 1]:
                            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if not(1664596800 <= time.time() <= 1667275200): return
        #if message.author.id != settings.OWNER_ID: return
        try:
            if not self.bot.enabled: return
            if not message.guild: return
            context = await self.bot.get_context(message)
            if context.valid: return

            blacklist_channels = {
                696766682546307193,
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
            
            if message.channel.id in blacklist_channels: return
            if message.channel.category_id in blacklist_categories: return

            if message.author.bot: return
            if len(self.required) < 1 and not self.queued:
                if message.author.id not in self.required:
                    self.required.append(message.author.id)
                return
            
            if not self.queued:
                self.queued = True
                self.required = []
                if os.environ["SHEPBOT_ENV"] == "testing":
                    await asyncio.sleep(5)
                else:
                    #await asyncio.sleep(5)
                    await asyncio.sleep(random.randint(60*5, 60*12.5))
                channel = self.bot.get_channel(settings.HALLOWEEN_CHANNEL)
                self.raiseerror = False
                self.active = []
                self.lookingfor = 1
                if random.random() > .95:
                    self.lookingfor = 2

                # to anyone that looks at this cog in the future
                # i'm extremely sorry for the next 100-ish lines
                # i needed to get 2 distribution systems done in 10 days and didn't have enough time to optimize
                # so as a result, this file is a mess

                message_type = random.randint(1, 2) # trick or treat
                self.mtype = message_type
                #announcement = await channel.send("(assume the thing happened here, add prose + other stuff later)" + str(message_type))
                embed = botembed("Trick or Treat!")
                person = random.choice(self.images)[:-4]
                prose = random.choice(["knocking at your door", "running to your doorstep", "with a look of mischief in their eyes", "with a bag of candy in their hands", "sneakily to your door"])
                if self.lookingfor == 1:
                    embed.description = f"**{person}** comes {prose}!\nThey want a **{'trick' if message_type == 1 else 'treat'}**!\nOpen the door and greet them with **`{settings.PREFIX}{'trick' if message_type == 1 else 'treat'}`**!"
                else:
                    embed.description = f"**{person}** comes {prose}!\nThey're carrying **two baskets**!\nThey want **{'trick' if message_type == 1 else 'treat'}s**!\nOpen the door and greet them with **`{settings.PREFIX}{'trick' if message_type == 1 else 'treat'}`**!\nThe first 2 people to do so get **double the rewards**!"
                file = discord.File(os.path.join(base, "assets", "halloween", "images", f"{person}.png"), filename=f"{person.replace(' ', '')}.png")
                embed.set_image(url=f"attachment://{person.replace(' ', '')}.png")
                announcement = await channel.send(embed=embed, file=file)
                
                descriptions = {
                    "Common": random.choice(["It's nothing special...", "It doesn't look like a whole lot...", "It's just okay."]), 
                    "Rare": random.choice(["It has a bit of weight to it.", "It's a bit worn down..."]), 
                    "Epic": random.choice(["It sparkles in the moonlight.", "It's *shiny*...", "You could probably sell it for a lot."]), 
                    "Legendary": random.choice(["You feel honored to recieve such a gift.", "It looks like it's glowing...?"])
                }

                try:
                    message = await self.bot.wait_for("message", check=self.check, timeout=60.0)
                except asyncio.TimeoutError:
                    await announcement.delete()
                    embed = botembed("No response...")
                    embed.description = f"**{person}** didn't receive anything, and left for another house."
                    embed.set_image(url=f"attachment://{person.replace(' ', '')}.png")
                    file = discord.File(os.path.join(base, "assets", "halloween", "images", f"{person}.png"), filename=f"{person.replace(' ', '')}.png")
                    await channel.send(embed=embed, file=file)
                    self.queued = False
                    self.raiseerror = True
                    self.active = []
                    self.lookingfor = 0
                    self.mtype = 0
                    return
                if self.lookingfor == 1:
                    c = message.content[1:].strip().lower()
                    if c != ["", "trick", "treat"][message_type]:
                        embed = botembed("Wrong Item!")
                        embed.description = f"You didn't give **{person}** what they wanted!\nThey left for another house."
                        embed.set_image(url=f"attachment://{person.replace(' ', '')}.png")
                        file = discord.File(os.path.join(base, "assets", "halloween", "images", f"{person}.png"), filename=f"{person.replace(' ', '')}.png")
                        await message.reply(embed=embed, file=file)
                        self.queued = False
                        self.raiseerror = True
                        self.active = []
                        self.lookingfor = 0
                        self.mtype = 0
                        return
                    if self.lookingfor == 1:
                        rarity = random.choices(["Common", "Rare", "Epic", "Legendary"], weights=self.weights)[0]
                        item = random.choice(self.items[rarity])
                        embed = botembed("Happy Halloween!")
                        description = descriptions[rarity] + f"\n\nThe item was added to your inventory. Use `{settings.PREFIX}inventory` to view it!"
                        
                        # this right here is the smartest thing i have written in 7 years
                        data = mh.find(self.hdb, message.author.id) # find the user data
                        if not data: # if the data doesn't exist:
                            data = {"_id": message.author.id, "common": 0, "rare": 0, "epic": 0, "legendary": 0} # make a completely blank data object
                            self.hdb.insert_one(data) # add it to the database

                        # discord uses a similar method for calculating role permissions (permissions -> permission integer)
                        idb = data[rarity.lower()] # get the item number for the specific rarity
                        bindata = bin(idb)[2:].rjust(len(self.items[rarity]), "0") # convert it to binary, and left-pad it with 0s to the length of the items list
                        # for any position i, a 1 indicates that the user has the i-th item in the items list for that rarity
                        # a 0 means that user doesn't have that item
                        temp = [c for c in bindata] # split string into individual characters
                        temp[self.items[rarity].index(item)] = "1" # set specific bit to 1 (user has the item)
                        temp = int("".join(temp), 2) # convert binary back into a number

                        if temp == idb: # if the number didn't change (i.e. the user already had the item)
                            description = f"\nYou already have this item!\nUse `{settings.PREFIX}inventory` to view it!"
                        else:
                            self.hdb.update_one({"_id": message.author.id}, {"$set": {rarity.lower(): temp}}) # update the database with the new item number
                        # this saves a *ton* of space in the database
                        # compared to saving every item string for every user
                        # hundreds of bytes per user vs. exactly 69 bytes per user
                        # saves storage and bandwidth, staying well below their respective limits

                        file = discord.File(os.path.join(base, "assets", "halloween", "images", f"{person}.png"), filename=f"{person.replace(' ', '')}.png")
                        embed.set_image(url=f"attachment://{person.replace(' ', '')}.png")            
                        embed.description = "\"Thank you for the " + c + "!\"\nIn return, you received a" + ("n" if rarity[0] in "AEIOU" else "") + " **`" + rarity + " " + item + "`**!\n" + description
                        await message.reply(embed=embed, file=file)
                        await message.add_reaction("🎃")
                else:
                    bad = False
                    for m in self.active:
                        c = m.content[1:].strip().lower()
                        if c != ["trick", "treat"][self.mtype - 1]:
                            bad = True
                            break
                    if bad:
                        embed = botembed("Wrong Item!")
                        embed.description = f"You didn't give **{person}** what they wanted!\nThey left for another house."
                        embed.set_image(url=f"attachment://{person.replace(' ', '')}.png")
                        file = discord.File(os.path.join(base, "assets", "halloween", "images", f"{person}.png"), filename=f"{person.replace(' ', '')}.png")
                        await message.reply(embed=embed, file=file)
                        self.queued = False
                        self.raiseerror = True
                        self.active = []
                        self.lookingfor = 0
                        self.mtype = 0
                        return
                    embed = botembed("Happy Halloween!")
                    istrings = []
                    for _ in range(2):
                        rarity = random.choices(["Common", "Rare", "Epic", "Legendary"], weights=self.weights)[0]
                        item = random.choice(self.items[rarity])
                        embed = botembed("Happy Halloween!")
                        description = descriptions[rarity]
                        istrings.append(f"• **`{rarity} {item}`** - {description}")
                        for m in self.active:
                            aid = m.author.id
                            data = mh.find(self.hdb, aid)
                            if not data:
                                data = {"_id": aid, "common": 0, "rare": 0, "epic": 0, "legendary": 0}
                                self.hdb.insert_one(data)
                            idb = data[rarity.lower()]
                            bindata = bin(idb)[2:].rjust(len(self.items[rarity]), "0")
                            temp = [c for c in bindata]
                            temp[self.items[rarity].index(item)] = "1"
                            temp = int("".join(temp), 2)

                            if temp != idb:
                                self.hdb.update_one({"_id": aid}, {"$set": {rarity.lower(): temp}})
                            
                    embed.description = f"\"Thank you for the {c}s!\"\nIn return, you received:\n" + "\n".join(istrings) + f"\n\nUse `{settings.PREFIX}inventory` to view your items!"
                    file = discord.File(os.path.join(base, "assets", "halloween", "images", f"{person}.png"), filename=f"{person.replace(' ', '')}.png")
                    embed.set_image(url=f"attachment://{person.replace(' ', '')}.png")   
                    await announcement.reply(f"<@{self.active[0].author.id}> <@{self.active[1].author.id}>", embed=embed, file=file)
                    for m in self.active:
                        await m.add_reaction("🎃")
                self.queued = False
                self.raiseerror = True
                self.active = []
                self.lookingfor = 0
                self.mtype = 0

            else:
                return
        except Exception as e:
            owner = self.bot.get_user(settings.OWNER_ID)
            tb = traceback.format_exc()
            if len(tb) > 4096:
                tb = tb[:4093] + "..."
            embed = functions.error("Command Error", f"Message: [Jump!]({message.jump_url})\n```{tb}```")
            await owner.send(embed=embed)


    @commands.command()
    async def inventory(self, ctx, rarity=None, page=1):
        if not(1664596800 <= time.time() <= 1667275200): return
        if not self.bot.enabled: return
        if rarity and page == 1:
            try:
                page = int(rarity)
                rarity = None
            except ValueError:
                pass
            else:
                rarity = None
        try:
            page = int(page)
        except ValueError:
            await ctx.send(embed=error("🚫 " + self.bot.response(2) +  f" you need to specify a valid page number (`1 - {pages}`)!"))
            return
        data = mh.find(self.hdb, ctx.author.id)
        if not data:
            await ctx.send(embed=error("You don't have any items!"))
            return

        if rarity:
            rarity = rarity.title()
            if rarity not in self.items:
                await ctx.send(embed=error("🚫 " + self.bot.response(2) +  f" you need to specify a valid rarity (`common`, `rare`, `epic`, or `legendary`)."))
                return
            #items = [i for i in items if i in self.items[rarity]]
            items = [self.items[rarity][i] for i in range(len(self.items[rarity])) if bin(data[rarity.lower()])[2:].rjust(len(self.items[rarity]), "0")[i] == "1"]
        else:
            items = []
            for r in self.items:
                items += [self.items[r][i] for i in range(len(self.items[r])) if bin(data[r.lower()])[2:].rjust(len(self.items[r]), "0")[i] == "1"]
            
        if not items:
            if rarity:
                await ctx.send(embed=error("🚫 " + self.bot.response(2) +  f" you don't have any items of that rarity!"))
            else:
                await ctx.send(embed=error("🚫 " + self.bot.response(2) +  f" you don't have any items!"))
            return
        items = sorted(items)
        pages = math.ceil(len(items) / 10)
        if page > pages:
            await ctx.send(embed=error("🚫 " + self.bot.response(2) +  f" you need to specify a valid page number (`1` through `{pages}`)!"))
            return
        viewed_items = items[(page-1)*10:page*10]

        embed = botembed("Inventory" + (f" ({rarity} Items)" if rarity else ""))
        embed.description = f"<@{ctx.author.id}> has {len(items)}{' **' + rarity.lower() + '**' if rarity else ''} item{'s' if len(items) != 1 else ''} in their inventory.\n(Page {page} of {pages})\n"
        for item in viewed_items:
            embed.description += "• **`" + item + "`**\n"
        embed.description = embed.description.strip()
        await ctx.send(embed=embed)

    @commands.command()
    async def ttleaderboard(self, ctx):
        if not(1664596800 <= time.time() <= 1667275200): return
        if not self.bot.enabled: return
        data = self.hdb.find()
        data = [d for d in data]
        data = sorted(data, key=lambda x: sum([bin(x[test])[1:].count("1") for test in x if test != "_id"]), reverse=True)
        embed = botembed("Halloween Leaderboard")
        embed.description = "Here are the top 10 users with the most items in their inventory!"
        for i, user in enumerate(data):
            if i == 10:
                break
            items = []
            for r in self.items:
                items += [self.items[r][i] for i in range(len(self.items[r])) if bin(user[r.lower()])[2:].rjust(len(self.items[r]), "0")[i] == "1"]
            embed.description += f"\n{i+1}. **<@{user['_id']}> - {len(items)} items**"

        await ctx.send(embed=embed)
        
        

async def setup(bot):
    await bot.add_cog(Halloween(bot))