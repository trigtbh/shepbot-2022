from discord.ext import commands
import functions
import random

def botembed(title):
    embed = functions.embed("Games - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Games", errormsg)
    return embed

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def coinflip(self, ctx):
        flip = random.choice(["Heads", "Tails"])
        embed = botembed("Coin Flip")
        embed.description = f"The coin landed on **{flip.upper()}**."
        return await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, notation=None):
        good = True
        params = notation.split("d")
        if params[0] == "":
            params[0] = "1"
        if params[1] == "":
            good = False
        else:
            try:
                times = int(params[0])
                sides = int(params[1])
            except:
                good = False
            else:
                if times < 1 or sides < 1:
                    good = False
        if not good:
            embed = error("Dice Roll")
            embed.description = "🚫 " + self.bot.response(2) + " you need to specify a valid [AdX dice notation](https://en.wikipedia.org/wiki/Dice_notation)."
            return await ctx.send(embed=embed)

        embed = botembed("Dice Roll")
        correct = "time" if times == 1 else "times"
        desc = f"You rolled a {sides}-sided die {times} {correct}.\n`"
        for _ in range(times):
            desc += str(random.randint(1, sides)) + ", "
        embed.description = desc[:-2] + "`"
        
        return await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def magic8ball(self, ctx, *, question=None):
        if not question:
            embed = error("8 Ball")
            embed.description = "🚫 " + self.bot.response(2) + " you need to enter a question."
            return await ctx.send(embed=embed)
        answers = ["It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."]
        reply = random.choice(answers)
        embed = botembed("8 Ball")
        embed.description = f"Question: `{question}`\nResponse: `{reply}`"
        return await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))