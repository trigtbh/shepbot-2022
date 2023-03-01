from discord.ext import commands
import functions
import urllib.request
import random
import json
import asyncio
import html
import settings

def botembed(title):
    embed = functions.embed("Trivia - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Trivia", errormsg)
    return embed

url = "https://opentdb.com/api.php?amount=1"

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    #async def cog_before_invoke(self, ctx: commands.Context):
    #    if ctx.author.id == settings.OWNER_ID:
    #        return ctx.command.reset_cooldown(ctx)

    @commands.cooldown(1, 0 if not settings.LOW_DATA_MODE else 30, commands.BucketType.user)
    @commands.command()
    async def trivia(self, ctx):
        embed = botembed("Question Asked")
        question = urllib.request.urlopen(url).read().decode(encoding='utf-8')
        #question = question.replace("&quot", "\"").replace("&#039;", "\'")
        try:
            question = json.loads(question)["results"][0]
        except Exception as e:
            print(str(e))
            print(question)
            embed = error("🚫 " + self.bot.response(2) + " there was an unknown error when getting the trivia question - please try running the command again.")
            return await ctx.send(embed=embed)
        desc = "❓ {} {}\n".format(self.bot.response(1), random.choice(["I got a good one for you!", "Here's a question!", "Let's see how you do against this!"]))
        desc = desc + "It's a{} `{}` question from the `{}` category.\n```{}{}```\n".format("n" if question["difficulty"][0] == "e" else "", question["difficulty"], question["category"], "T/F: " if question["type"] == "boolean" else "", self.humanize(question["question"]))
        
        paired = {}
        reverse = {}
        
        if question["type"] == "boolean":
            desc = desc + "`T`: True\n`F`: False\n"
            paired["t"] = "True"
            paired["f"] = "False"
        else:
            answers = [question["correct_answer"]] + question["incorrect_answers"]
            random.shuffle(answers)
            for a in range(len(answers)):
                desc = desc + "`{}`: {}\n".format("ABCD"[a], self.humanize(answers[a]))
                paired["abcd"[a]] = answers[a]
                reverse[answers[a]] = "abcd"[a]
        
        
            
        times = {  # harder question -> more time
            "easy": 15,
            "medium": 20,
            "hard": 25
        }

        desc = desc + "You have `{}` seconds. {}".format(times[question["difficulty"]], random.choice(["You got this!", "I believe in you!", "You can do this!"]))
        embed.description = desc

        message = await ctx.send(embed=embed)

        def check(message):
            if message.author == ctx.message.author and message.channel == ctx.channel:
                content = message.content.strip().lower()
                if content[0] in paired.keys():
                    return True
        
        try:
            m = await self.bot.wait_for("message", check=check, timeout=times[question["difficulty"]])
        except asyncio.TimeoutError:
            embed = botembed("Time's Up!")
            embed.description = "❓ Time's up! Unfortunately, you didn't answer the question in time."
            await message.edit(embed=embed)
        else:
            content = m.content.strip().lower()
            if paired[content[0]] == question["correct_answer"]:
                embed = botembed("Win")
                embed.description = "{} You got that {}!\nThe answer was `{}`.".format(self.bot.response(5), random.choice(["correct", "right"]), self.humanize(question["correct_answer"]))
                return await ctx.send(embed=embed)
            else:
                embed = botembed("Loss")
                embed.description = "{} that wasn't the correct answer.\nThe correct answer was `{}`.".format(self.bot.response(2), self.humanize(question["correct_answer"]))
                return await ctx.send(embed=embed)

    def humanize(self, string):
        return html.unescape(string) # fixes weird character conversion

async def setup(bot):
    await bot.add_cog(Trivia(bot))