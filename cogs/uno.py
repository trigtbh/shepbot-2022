# in all honesty idk how this is gonna be done lmao

import discord
from discord.ext import commands
import asyncio
import random
import settings
import multiplayer as mp
import functions

def botembed(title):
    embed = functions.embed("Uno - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Uno", errormsg)
    return embed

def get_deck():
    deck = []
    for _ in range(2):
        for color in ("Red", "Blue", "Green", "Yellow"):
            for number in range(0, 10):
                deck.append(f"{color} {number}")
            for action in ("Skip", "Reverse", "Draw 2"):
                deck.append(f"{color} {action}")
    for _ in range(4):
        for action in ("Wild", "Draw 4"):
            deck.append(f"{action}")
    return deck

def draw(hand, deck, discard, amount=1):
    for _ in range(amount):
        try:
            hand.append(deck.pop(0))
        except IndexError:
            deck = discard[:-1]
            random.shuffle(deck)
            discard = [discard[-1]]
            hand.append(deck.pop(0))
    return hand

def get_valid_moves(hand, discard, color, increment):
    valid_moves = ["Draw " + (str(increment) + " cards" if increment > 1 else "a card")]
    if discard[-1] == "Draw 4":
        return [f"Draw {increment} cards"]
    elif increment > 0 and discard[-1] != "Draw 4":
        for card in hand:
            if "Draw" in card:
                valid_moves.append(card)
    else:
        for card in list(set(hand)):
            if card == "Wild" or card == "Draw 4":
                valid_moves.append(card)
            else:
                if discard in ("Wild", "Draw 4"):
                    if card.split()[0] == color:
                        valid_moves.append(card)
                else:
                    if card.split()[0] == color:
                        valid_moves.append(card)
                    elif card.split()[1] == discard.split()[1]:
                        valid_moves.append(card)
    return valid_moves



class Uno(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ims = {}
        self.responded = {}
        self.start = {}
        self.playing = []
        
    @commands.command()
    async def uno(self, ctx, members: commands.Greedy[discord.Member]=None):
        if members is not None: # basic invite handler
            if ctx.author.id in self.responded or ctx.author.id in self.playing:
                embed = error("🚫 " + self.bot.response(2) + " you already have a game running!")
                return await ctx.send(embed=embed)

            self.ims[ctx.author.id] = mp.InviteManager(self, self.bot, ctx, "Uno")
            self.responded[ctx.author.id] = False
            self.start[ctx.author.id] = False
            embed = botembed("Invite Menu")
            embed.description = "🎮 Waiting to send invites..."
            m = await ctx.send(embed=embed, view=mp.GameMenu(manager=self.ims[ctx.author.id], mid=ctx.author.id, required=1))
            self.ims[ctx.author.id].m = m
            for member in members:
                await self.ims[ctx.author.id].invite(member)
            while not self.responded[ctx.author.id]:
                await asyncio.sleep(0.01)
            if not self.start[ctx.author.id]:
                del self.responded[ctx.author.id]
                del self.start[ctx.author.id]
                del self.ims[ctx.author.id]
                return
            await m.delete()
            players = [await commands.MemberConverter().convert(ctx, str(u)) for u in self.ims[ctx.author.id].players]
        else:
            players = [ctx.message.author]
        random.shuffle(players)

        game = []

        deck = get_deck()
        random.shuffle(deck)
        discard = [deck.pop(0)]
        while discard[-1] == "Wild" or discard[-1] == "Draw 4":
            discard.append(deck.pop(0))

        for p in players:
            self.playing.append(p)
            game.append({"player": p.id, "hand": draw([], deck, discard, amount=7), "is_random": False})
        if len(players) == 1:
            for i in range(3):
                game.append({"player": "CPU " + str(i + 1), "hand": draw([], deck, discard, amount=7), "is_random": True})

        random.shuffle(game)

        embed = botembed("Game Started")
        desc = "🃏 " + self.bot.response(1) + f" I started a game of Uno.\nAll players have been dealt 7 cards.\nThe order of play is as follows:"
        for c, player in enumerate(game):
            desc = desc + f"\n{c + 1}: {'<@' + str(player['player']) + '>' if not player['is_random'] else player['player']}"
        desc = desc + "\n\nThe game will start in 10 seconds."
        embed.description = desc
        await ctx.send(embed=embed)
        await asyncio.sleep(10)
        turn = 0
        index = 0
        direction = 1
        increment = 0
        color = discard[0].split()[0]
        


        while True:
            ncolor = ""
            embed = botembed("Turn " + str(turn + 1))
            description = f"🎲 It is now {'<@' + str(game[index]['player']) + '>' if not game[index]['is_random'] else game[index]['player']}'s turn.\nWaiting for a response..."
            embed.description = description
            embed.add_field(name="Deck", value=f"{len(deck)} cards left", inline=False)
            embed.add_field(name="Discard", value=discard[-1] + ((' and `' + str(len(discard) - 1) + '` other card') if len(discard) - 1 > 0 else '') + ('s' if len(discard) - 1 > 1 else ''), inline=False)
            embed.add_field(name="Hands", value="\n".join([f"{'<@' + str(player['player']) + '>' if not player['is_random'] else player['player']}: {len(player['hand'])} card{'s' if len(player['hand']) != 1 else ''}" for player in game]), inline=False)
            message = await ctx.send(embed=embed)
            if game[index]['is_random']:
                valid_moves = get_valid_moves(game[index]['hand'], discard[-1], color, increment)
                play = random.choice(valid_moves)
                if play == "Wild" or play == "Draw 4":
                    ncolor = random.choice(["Red", "Blue", "Green", "Yellow"])
                await asyncio.sleep(3)
            else:
                valid_moves = get_valid_moves(game[index]['hand'], discard[-1], color, increment)
                hand = game[index]['hand'].copy()
                hand = sorted(list(dict.fromkeys(hand).keys()))
                hand.insert(0, valid_moves[0])
                choose_from = []
                newembed = botembed("Your Turn")
                desc = f"🎲 It is now your turn.\nThe current card is a `{discard[-1]}`{('. The current color is `' + color + '`') if discard[-1] in {'Wild', 'Draw 4'} else ''}\nHere are your options:\n"
                maxval = 0
                for i, card in enumerate(hand):
                    if card in valid_moves:
                        maxval += 1
                        desc = desc + f"{maxval}: **{card}**{' (x' + str(game[index]['hand'].count(card)) + ')' if game[index]['hand'].count(card) > 1 else ''}\n"
                        choose_from.append(card)
                    else:
                        desc = desc + f"- {card}{' (x' + str(game[index]['hand'].count(card)) + ')' if game[index]['hand'].count(card) > 1 else ''}\n"
                desc = desc + "\nType the number of the action you want to play."
                newembed.description = desc
                user = self.bot.get_user(game[index]['player'])
                test = await user.send(embed=newembed)
                def check(m):
                    if m.author.id == game[index]['player'] and m.channel.id == test.channel.id:
                        try:
                            val = int(m.content)
                            if val > 0 and val <= maxval:
                                return True
                        except:
                            return False
                    return False
                getplay = await self.bot.wait_for('message', check=check)
                play = choose_from[int(getplay.content) - 1]
                if play == "Wild" or play == "Draw 4":
                    newembed = botembed("Wild Card")
                    newembed.description = "🎲 You have played a wild card.\nPlease choose a color (`Red`, `Yellow`, `Blue`, `Green`)."
                    await user.send(embed=newembed)
                    def check(m):
                        if m.author.id == game[index]['player'] and m.channel.id == test.channel.id:
                            if m.content.lower() in ["red", "blue", "green", "yellow"]:
                                return True
                        return False
                    cmessage = await self.bot.wait_for('message', check=check)
                    ncolor = cmessage.content.title()
            if play == "Draw a card":
                game[index]['hand'] = draw(game[index]['hand'], deck, discard)
                embed = botembed("Turn " + str(turn + 1))
                description = f"🎲 It is now {'<@' + str(game[index]['player']) + '>' if not game[index]['is_random'] else game[index]['player']}'s turn.\nThey decided to draw a card.\nThe next turn will begin in 10 seconds."
                embed.description = description
                embed.add_field(name="Deck", value=f"{len(deck)} cards left", inline=False)
                embed.add_field(name="Discard", value=discard[-1] + ((' and `' + str(len(discard) - 1) + '` other card') if len(discard) - 1 > 0 else '') + ('s' if len(discard) - 1 > 1 else ''), inline=False)
                embed.add_field(name="Hands", value="\n".join([f"{'<@' + str(player['player']) + '>' if not player['is_random'] else player['player']}: {len(player['hand'])} card{'s' if len(player['hand']) != 1 else ''}" for player in game]), inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(10)
                turn += 1
                index += direction
                if index >= len(game):
                    index = 0
                elif index < 0:
                    index = len(game) - 1
                continue
            elif play.startswith("Draw ") and play.endswith(" cards"):
                game[index]['hand'] = draw(game[index]['hand'], deck, discard, amount=int(play.split()[1]))
                embed = botembed("Turn " + str(turn + 1))
                description = f"🎲 It is now {'<@' + str(game[index]['player']) + '>' if not game[index]['is_random'] else game[index]['player']}'s turn.\nThey decided to draw {play.split()[1]} cards.\nThe next turn will begin in 10 seconds."
                embed.description = description
                embed.add_field(name="Deck", value=f"{len(deck)} cards left", inline=False)
                embed.add_field(name="Discard", value=discard[-1] + ((' and `' + str(len(discard) - 1) + '` other card') if len(discard) - 1 > 0 else '') + ('s' if len(discard) - 1 > 1 else ''), inline=False)
                embed.add_field(name="Hands", value="\n".join([f"{'<@' + str(player['player']) + '>' if not player['is_random'] else player['player']}: {len(player['hand'])} card{'s' if len(player['hand']) != 1 else ''}" for player in game]), inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(10)
                turn += 1
                index += direction
                increment = 0
                if index >= len(game):
                    index = 0
                elif index < 0:
                    index = len(game) - 1
                continue
            
            embed = botembed("Turn " + str(turn + 1))
            description = f"🎲 It is now {'<@' + str(game[index]['player']) + '>' if not game[index]['is_random'] else game[index]['player']}'s turn.\nThey played a **{play}**."
            embed.add_field(name="Deck", value=f"{len(deck)} cards left", inline=False)
            game[index]['hand'].remove(play)
            discard.append(play)
            if play not in {'Wild', 'Draw 4'}:
                color = play.split()[0]
            embed.add_field(name="Discard", value=discard[-1] + ((' and `' + str(len(discard) - 1) + '` other card') if len(discard) - 1 > 0 else '') + ('s' if len(discard) - 1 > 1 else ''), inline=False)
            embed.add_field(name="Hands", value="\n".join([f"{'<@' + str(player['player']) + '>' if not player['is_random'] else player['player']}: {len(player['hand'])} card{'s' if len(player['hand']) != 1 else ''}" for player in game]), inline=False)
            if ncolor:
                color = ncolor
                description = description + f"\nThe color has been set to **`{color}`**."
            
            if len(game[index]['hand']) == 0:
                embed = botembed("Game Over")
                embed.description = f"🎲 It is now {'<@' + str(game[index]['player']) + '>' if not game[index]['is_random'] else game[index]['player']}'s turn.\nThey played a **{play}**.\n{'<@' + str(game[index]['player']) + '>' if not game[index]['is_random'] else game[index]['player']} has won the game!"
            
                await message.edit(embed=embed)
                if ctx.author.id in self.responded: del self.responded[ctx.author.id]
                if ctx.author.id in self.responded: del self.start[ctx.author.id] # redundant but necessary for some reason?
                if ctx.author.id in self.responded: del self.ims[ctx.author.id]
                for player in game:
                    if not player['is_random'] and player['player'] in self.playing:
                        self.playing.remove(player['player'])
                return
                

            if len(game[index]['hand']) == 1:
                description = description + "\nThey have **1** card left.\n**Call `Uno` in the next 10 seconds and they will be forced to draw 2 cards.**"
                embed.description = description
                await message.edit(embed=embed)
                def check(m):
                    if m.channel.id == message.channel.id and m.author.id in [player['player'] for player in game]:
                        if m.content.lower() == "uno":
                            return True
                try:
                    unocheck = await self.bot.wait_for('message', check=check, timeout=10)
                except:
                    pass
                else:
                    if unocheck.author.id != game[index]['player']:
                        game[index]['hand'] = draw(game[index]['hand'], deck, discard, 2)
                        embed = botembed("Turn " + str(turn + 1))
                        description = f"🎲 It is now {'<@' + str(game[index]['player']) + '>' if not game[index]['is_random'] else game[index]['player']}'s turn.\nThey played a **{play}**.\nThey did not call Uno and were forced to draw 2 cards."
                        embed.description = description
                        embed.add_field(name="Deck", value=f"{len(deck)} cards left", inline=False)
                        embed.add_field(name="Discard", value=discard[-1] + ((' and `' + str(len(discard) - 1) + '` other card') if len(discard) - 1 > 0 else '') + ('s' if len(discard) - 1 > 1 else ''), inline=False)
                        embed.add_field(name="Hands", value="\n".join([f"{'<@' + str(player['player']) + '>' if not player['is_random'] else player['player']}: {len(player['hand'])} card{'s' if len(player['hand']) != 1 else ''}" for player in game]), inline=False)
                        await message.edit(embed=embed)
                        await asyncio.sleep(10)
                        turn += 1
                        index += direction
                        if index >= len(game):
                            index = 0
                        elif index < 0:
                            index = len(game) - 1
                        continue
                    else:
                        turn += 1
                        index += direction
                        if index >= len(game):
                            index = 0
                        elif index < 0:
                            index = len(game) - 1
                        continue
            if play.endswith("Draw 2"):
                increment += 2
            elif play.endswith("Draw 4"):
                increment += 4
            elif play.endswith("Skip"):
                description = description + "\n**The next player was skipped.**"
            elif play.endswith("Reverse"):
                description = description + "\n**The direction of play has been reversed.**"
                direction *= -1
            
            description = description + "\nThe next turn will begin in 10 seconds."
            embed.description = description
            await message.edit(embed=embed)

            if play.endswith("Skip"):
                index += (direction * 2)
                if index >= len(game):
                    index = 0
                elif index < 0:
                    index = len(game) - 1
            else:
                index += direction
                if index >= len(game):
                    index = 0
                elif index < 0:
                    index = len(game) - 1
            turn += 1
            await asyncio.sleep(10)



async def setup(bot):
    await bot.add_cog(Uno(bot))