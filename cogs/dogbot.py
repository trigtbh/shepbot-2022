import discord
from discord.ext import commands
import os
import csv
import functions
import settings
import asyncio
import datetime
import time
import humanize

base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def botembed(title):
    embed = functions.embed("Pets - " + title, color=0x57ffb6)
    return embed

class PetBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.breeds = {}
        self.db = self.bot.pymongodb["MainDatabase"]["pets"]
        with open(os.path.join(base, "assets", "PetBreeds.csv")) as csvfile:
            r = csv.reader(csvfile)
            i = 0
            for row in r:
                if i == 0:
                    i += 1
                    continue
                self.breeds[row[0]] = {"size": int(row[1]), "energy": int(row[2]), "trainability": int(row[3]), "attitude": int(row[4])}
        self.breeds = {k: self.breeds[k] for k in sorted(self.breeds)}
    
    @commands.group()
    async def pet(self, ctx):
        if ctx.invoked_subcommand is None:

            member = ctx.author

            if len(list(self.db.find({"_id": member.id}))) == 0:
                if member.id != ctx.author.id:
                    embed = functions.error("Pet Menu", "🚫 " + self.bot.response(2) + f" {member.mention} does not have a pet.")
                    return await ctx.send(embed=embed)
                embed = botembed("Pet Not Found")
                embed.description = "You do not have a pet yet. Would you like to get one?\nReact with ✅ within 60 seconds to open the menu."
                m = await ctx.send(embed=embed)
                await m.add_reaction("✅")
                try:
                    await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id and str(r.emoji) == "✅", timeout=60.0)
                except:
                    embed = botembed("Pet Not Found")
                    embed.description = "You did not react in time.\nPlease run the command again to reopen the menu."
                    return await m.edit(embed=embed)
                embed = botembed("Pet Menu (Breed)")
                embed.description = f"Please enter the number of the breed you would like to get.\nUse `{settings.PREFIX}pet breeds` to see a list of breeds.\nEnter `cancel` to cancel."
                try:
                    m = await ctx.author.send(embed=embed)
                except:
                    m = await ctx.send(embed=embed)
                def check(message):
                    if not (message.author.id == ctx.author.id and message.channel.id == m.channel.id):
                        return False
                    if message.content.lower().strip() == "cancel":
                        return True
                    try:
                        int(message.content)
                    except:
                        return False
                    if int(message.content) < 1 or int(message.content) > len(self.breeds):
                        return False
                    return True
                try:
                    message = await self.bot.wait_for("message", check=check, timeout=60.0)
                except:
                    embed = botembed("Pet Menu (Breed)")
                    embed.description = "You did not enter a breed in time.\nPlease run the command again to reopen the menu."
                    return await m.edit(embed=embed)
                if message.content.lower().strip() == "cancel":
                    embed = botembed("Pet Menu (Breed)")
                    embed.description = "You have cancelled the menu.\nPlease run the command again to reopen the menu."
                    return await m.edit(embed=embed)
                breed = list(self.breeds.keys())[int(message.content) - 1]
                embed = botembed("Pet Menu (Name)")
                embed.description = f"Please enter the name of your `{breed}`.\nEnter `cancel` to cancel."
                m = await m.channel.send(embed=embed)
                def check(message):
                    if not (message.author.id == ctx.author.id and message.channel.id == m.channel.id):
                        return False
                    if message.content.lower().strip() == "cancel":
                        return True
                    return True
                try:
                    message = await self.bot.wait_for("message", check=check, timeout=60.0)
                except:
                    embed = botembed("Pet Menu (Name)")
                    embed.description = "You did not enter a name in time.\nPlease run the command again to reopen the menu."
                    return await m.edit(embed=embed)
                if message.content.lower().strip() == "cancel":
                    embed = botembed("Pet Menu (Name)")
                    embed.description = "You have cancelled the menu.\nPlease run the command again to reopen the menu."
                    return await m.edit(embed=embed)
                name = message.content
                embed = botembed("Pet Menu (Confirm)")
                embed.description = f"Please confirm that you would like to get  a{'n' if breed[0].lower() in {'a', 'e', 'i', 'o', 'u'} else ''} `{breed}` named `{name}`.\nReact with ✅ to confirm.\nReact with ❌ to cancel."
                m = await m.channel.send(embed=embed)
                await m.add_reaction("✅")
                await m.add_reaction("❌")
                try:
                    r = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id and str(r.emoji) in ["✅", "❌"], timeout=60.0)
                except:
                    embed = botembed("Pet Menu (Confirm)")
                    embed.description = "You did not react in time.\nPlease run the command again to reopen the menu."
                    return await m.edit(embed=embed)
                if str(r[0].emoji) == "❌":
                    embed = botembed("Pet Menu (Confirm)")
                    embed.description = "You have cancelled the menu.\nPlease run the command again to reopen the menu."
                    return await m.edit(embed=embed)
                self.db.insert_one({
                    "_id": ctx.author.id,
                    "breed": breed,
                    "name": name,
                    "size": self.breeds[breed]["size"],
                    "energy": self.breeds[breed]["energy"],
                    "trainability": self.breeds[breed]["trainability"],
                    "attitude": self.breeds[breed]["attitude"],
                    "happiness": 100,
                    "hunger": 100,
                    "thirst": 100,
                    "cleanliness": 100,
                    "lastfed": time.time(),
                    "lastwatered": time.time(),
                    "lastcleaned": time.time(),
                    "lastplayed": time.time(),
                    "birthdate": time.time()
                })
                embed = botembed("Pet Menu (Confirm)")
                embed.description = f"You successfully got a{'n' if breed[0].lower() in {'a', 'e', 'i', 'o', 'u'} else ''} {breed} named {name}!\nUse `{settings.PREFIX}pet` to check up on them every so often.\nIf they get hungry, use `{settings.PREFIX}pet feed` to feed them.\nIf they get thirsty, use `{settings.PREFIX}pet water` to give them water.\nIf they get dirty, use `{settings.PREFIX}pet clean` to clean them.\nIf they get bored, use `{settings.PREFIX}pet play` to play with them."
                await m.channel.send(embed=embed)
            else:
                pet = list(self.db.find({"_id": ctx.author.id}))[0]

                trainability = pet["trainability"]
                size = pet["size"]
                energy = pet["energy"]

                # Update pet
                pet["happiness"] = int(max(min(100, 100 - (time.time() - pet["lastplayed"]) / 3600 * 5), 0))
                pet["hunger"] = int(max(0, min(100, 100 - (time.time() - pet["lastfed"]) / 3600 * (size + energy // 2))))
                pet["thirst"] = int(max(0, min(100, 100 - (time.time() - pet["lastwatered"]) / 3600 * (size * 1.5))))
                pet["cleanliness"] = int(max(0, min(100, 100 - (time.time() - pet["lastcleaned"]) / 3600 * (size))))

                leave_reasons = []
                if pet["happiness"] == 0:
                    leave_reasons.append("boredom")
                if pet["hunger"] == 0:
                    leave_reasons.append("hunger")
                if pet["thirst"] == 0:
                    leave_reasons.append("thirst")
                if pet["cleanliness"] == 0:
                    leave_reasons.append("being dirty")

                if leave_reasons:
                    embed = botembed("Oh no!")
                    if len(leave_reasons) == 1:
                        embed.description = f"Your pet ran away due to {leave_reasons[0]}!"
                    elif len(leave_reasons) == 2:
                        embed.description = f"Your pet ran away due to {leave_reasons[0]} and {leave_reasons[1]}!"
                    else:
                        embed.description = f"Your pet ran away due to {', '.join(leave_reasons[:-1])}, and {leave_reasons[-1]}!"
                    try:
                        await ctx.author.send(embed=embed)
                    except:
                        await ctx.send(embed=embed)
                    self.db.delete_one({"_id": ctx.author.id})
                    return

                status = ""
                if pet["happiness"] < 25:
                    status = "Sad"
                elif pet["happiness"] < 50:
                    status = "Bored"
                elif pet["happiness"] < 75:
                    status = "Happy"
                
                if pet["hunger"] < 25:
                    status = status + ", starving"
                elif pet["hunger"] < 50:
                    status = status + ", hungry"
                elif pet["hunger"] < 75:
                    status = status + ", full"
                
                if pet["thirst"] < 25:
                    status = status + ", thirsty"
                elif pet["thirst"] < 50:
                    status = status + ", thirsty"
                elif pet["thirst"] < 75:
                    status = status + ", hydrated"

                if pet["cleanliness"] < 25:
                    status = status + ", dirty"
                elif pet["cleanliness"] < 50:
                    status = status + ", dirty"
                elif pet["cleanliness"] < 75:
                    status = status + ", clean"
                

                embed = botembed(f"{ctx.author.name}'s Pet")
                dt = time.time() - pet["birthdate"]
                age = humanize.precisedelta(datetime.timedelta(seconds=dt), suppress=['seconds'], format='%0.0f') 
                embed.add_field(name="__Info__", value=f"**Name:** {pet['name']}\n**Breed:** {pet['breed']}\n**Size:** {pet['size']}\n**Energy:** {pet['energy']}/10\n**Trainability:** {pet['trainability']}/10\n**Attitude:** {pet['attitude']}/10\n**Age:** {age}", inline=False)
                embed.add_field(name="__Stats__", value=f"**Happiness:** {pet['happiness']}/100\n**Hunger:** {pet['hunger']}/100\n**Thirst:** {pet['thirst']}/100\n**Cleanliness:** {pet['cleanliness']}/100", inline=False)
                await ctx.send(embed=embed)


    

    @pet.command()
    async def feed(self, ctx):
        if not list(self.db.find({"_id": ctx.author.id})):
            embed = botembed("Feed")
            embed.description = f"You do not have a pet yet.\nPlease run `{settings.PREFIX}pet` to get one."
            await ctx.send(embed=embed)
        else:
            pet = list(self.db.find({"_id": ctx.author.id}))[0]
            if pet["hunger"] >= 75:
                embed = botembed("Feed")
                embed.description = f"{pet['name']} is not hungry."
                await ctx.send(embed=embed)
            else:
                embed = botembed("Feed")
                embed.description = f"You fed {pet['name']}!\nThey are no longer hungry."
                await ctx.send(embed=embed)
                self.db.update_one({"_id": ctx.author.id}, {"$set": {"hunger": 100, "lastfed": time.time()}})

    @pet.command()
    async def water(self, ctx):
        if not list(self.db.find({"_id": ctx.author.id})):
            embed = botembed("Water")
            embed.description = f"You do not have a pet yet.\nPlease run `{settings.PREFIX}pet` to get one."
            await ctx.send(embed=embed)
        else:
            pet = list(self.db.find({"_id": ctx.author.id}))[0]
            if pet["thirst"] >= 75:
                embed = botembed("Water")
                embed.description = f"{pet['name']} is not thirsty."
                await ctx.send(embed=embed)
            else:
                embed = botembed("Water")
                embed.description = f"You gave water to {pet['name']}!\nThey are no longer thirsty."
                await ctx.send(embed=embed)
                self.db.update_one({"_id": ctx.author.id}, {"$set": {"thirst": 100, "lastwatered": time.time()}})

    @pet.command()
    async def clean(self, ctx):
        if not list(self.db.find({"_id": ctx.author.id})):
            embed = botembed("Clean")
            embed.description = f"You do not have a pet yet.\nPlease run `{settings.PREFIX}pet` to get one."
            await ctx.send(embed=embed)
        else:
            pet = list(self.db.find({"_id": ctx.author.id}))[0]
            if pet["cleanliness"] >= 75:
                embed = botembed("Clean")
                embed.description = f"{pet['name']} is not dirty."
                await ctx.send(embed=embed)
            else:
                embed = botembed("Clean")
                embed.description = f"You cleaned {pet['name']}!\nThey are no longer dirty."
                await ctx.send(embed=embed)
                self.db.update_one({"_id": ctx.author.id}, {"$set": {"cleanliness": 100, "lastcleaned": time.time()}})

    @pet.command()
    async def play(self, ctx):
        if not list(self.db.find({"_id": ctx.author.id})):
            embed = botembed("Play")
            embed.description = f"You do not have a pet yet.\nPlease run `{settings.PREFIX}pet` to get one."
            await ctx.send(embed=embed)
        else:
            pet = list(self.db.find({"_id": ctx.author.id}))[0]
            if pet["happiness"] >= 75:
                embed = botembed("Play")
                embed.description = f"{pet['name']} is not bored."
                await ctx.send(embed=embed)
            else:
                embed = botembed("Play")
                embed.description = f"You played with {pet['name']}!\nThey are no longer bored."
                await ctx.send(embed=embed)
                self.db.update_one({"_id": ctx.author.id}, {"$set": {"happiness": 100, "lastplayed": time.time()}})

    @pet.command()
    async def breeds(self, ctx, d=None):
        chose_good = True
        if not d:
            chose_good = False
        else:
            try:
                d = int(d)
            except:
                chose_good = False
            else:
                if not(1 <= d <= len(self.breeds.keys())):
                    chose_good = False
        if not chose_good:
            embed = botembed("Breeds")
            desc = "🐶 Here are the available breeds:\n"
            for count, k in enumerate(self.breeds.keys()):
                desc = desc + "\t**" + str(count + 1) + ":** " + k + "\n"
            desc = desc + f"Use `{settings.PREFIX}pet breeds [breed number]` for more info on a specific breed."
            embed.description = desc
            await ctx.send(embed=embed)
        else:
            d -= 1
            breed_name = list(self.breeds.keys())[d]
            breed_info = self.breeds[breed_name]
            embed = botembed("Breed Info")
            desc = "🐶 Here is the info for **" + breed_name + "**:\n\n"
            desc = desc + "\t**Size: **`" + ["Small", "Medium", "Large"][int(breed_info["size"]) - 1] + "`\n"
            desc = desc + "\t**Energy: **`" + str(breed_info["energy"]) + "/10`\n"
            desc = desc + "\t**Trainability: **`" + str(breed_info["trainability"]) + "/10`\n"
            desc = desc + "\t**Attitude: **" + str(breed_info["attitude"]) + "/10`\n"
            embed.description = desc
            await ctx.send(embed=embed)

    

async def setup(bot):
    await bot.add_cog(PetBot(bot))