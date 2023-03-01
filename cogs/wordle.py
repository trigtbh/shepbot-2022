from discord.ext import commands
import functions
import random
import asyncio
import os

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def botembed(title):
    embed = functions.embed("Word Guess - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Word Guess", errormsg)
    return embed



class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(path, "assets", "words.txt")) as f:
            self.words = [x.lower().strip() for x in f.readlines()]
        self.games = {}

    def process(self, guess, correct):
        guess = guess.lower().strip()
        correct = correct.lower().strip()
        toreturn = ""
        for i in range(len(guess)):
            if guess[i] == correct[i]:
                toreturn = toreturn + "🟩" + guess[i].upper() + " " # this could be done with ansi escape codes but those don't render properly on mobile
            elif guess[i] in correct:
                toreturn = toreturn + "🟧" + guess[i].upper() + " "
            else:
                toreturn = toreturn + "⬛" + guess[i].upper() + " "
        return toreturn.strip()

    @commands.command(aliases=["wg", "wordguess"])
    async def word_guess(self, ctx):
        if ctx.author.id in self.games:
            embed = error("🚫 " + self.bot.response(2) + f" [you're currently playing a game right now]({self.games[ctx.author.id].jump_url}).\nIf you want to end it, type `end`.")
            return await ctx.send(embed=embed)

        async def inner(message):
            message = ctx.message
            content = message.content.strip().lower()
            reduced = "".join([c for c in content if c in "qwertyuiopasdfghjklzxcvbnm"])
            if len(reduced) == len(content) == 5:
                if reduced not in self.words:
                    await message.add_reaction("❌")

        def check(message):
            content = message.content.strip().lower()
            reduced = "".join([c for c in content if c in "qwertyuiopasdfghjklzxcvbnm"])
            if message.author.id not in self.games:
                return False
            if message.channel.id != self.games[message.author.id].channel.id:
                return False
            if len(reduced) == len(content) == 5:
                if reduced in self.words:
                    return True
                else:
                    asyncio.create_task(message.add_reaction("❌"))
                    return False

            if content == "end":
                return True

            return False

        word = random.choice(self.words).strip().lower()
        guessed = []
        
        won = False

        for i in range(6):
            embed = botembed(f"Round {i+1}/6")
            text = "```\n"
            for g, guess in enumerate(guessed):
                text = text + str(g + 1) + ": " + self.process(guess, word) + "\n"
            text = text + "```"

            embed.description = text
                
            m = await ctx.send(embed=embed)
            self.games[ctx.author.id] = m
            message = await self.bot.wait_for("message", check=check)
        
            c = message.content.strip().lower()
            if c == "end":
                del self.games[ctx.author.id]
                embed = botembed("Game Ended")
                embed.description = "📤 " + self.bot.response(1) + " I ended your current game."
                return await ctx.send(embed=embed)
            guessed.append(c.upper())
            if c == word:
                won = True
                break
            
        
        del self.games[ctx.author.id]
        if won:
            embed = botembed("Win")
            embed.description = "🏆 " + self.bot.response(1) + " `" + word.upper() + "` was the correct word."
        else:
            embed = botembed("Loss")
            embed.description = "⁉️ " + self.bot.response(2) + " `" + word.upper() + "` was the correct word."
        text = "```\n"
        for g, guess in enumerate(guessed):
            text = text + str(g + 1) + ": " + self.process(guess, word) + "\n"
        text = text + "```"
        embed.description = embed.description + "\n" + text
        return await ctx.send(embed=embed)    
        


async def setup(bot):
    await bot.add_cog(Wordle(bot))