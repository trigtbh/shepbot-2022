from discord.ext import commands
import discord
import functions
import multiplayer as mp
import asyncio
import random

# boilerplate extravaganza

def botembed(title):
    embed = functions.embed("Blackjack - " + title, color=0x8f0000)
    return embed

def error(errormsg):
    embed = functions.error("Blackjack", errormsg)
    return embed

def get_value(hand): # converts a hand into a score value
    value = 0
    vs = {}
    for i in range(2, 11):
        vs[str(i)] = i
    vs["J"] = 10
    vs["Q"] = 10
    vs["K"] = 10
    vs["A2"] = 1
    vs["A"] = 11
    has_a = False
    for card in hand:
        c_v = card[1:]
        value += vs[c_v]
    return value

def hit(hand, deck): # adds a card to a hand and calculates if it busted or not
    bust = False
    card = random.choice(deck)
    deck.remove(card)
    new = hand + [card]
    v = get_value(new)
    if v <= 21:
        hand = new
    else:
        if card[1] == "A":
            fixed = hand + [card+"2"]
            v = get_value(fixed)
            if v <= 21:
                hand = fixed
            else:
                bust = True
        else:
            index = [hand.index(c) for c in hand if len(c) == 2 and c[1] == "A"]
            if len(index) > 0:
                hand[index[0]] = hand[index[0]][0] + "A2"
                fixed2 = hand + [card]
                v = get_value(fixed2)
                if v <= 21:
                    hand = fixed2
                else:
                    bust = True
            else:
                hand = new
                bust = True
    return hand, deck, bust

def process_hand(hand, mask=False): # human readable hand
    h = []
    for c in hand:
        if len(c) == 3:
            if c[-1] == "2":
                c = c[:2]

        h.append(c.replace("S", "♠").replace("D", "♦").replace("C", "♣").replace("H", "♥"))
    if mask:
        h = [h[0]] + (["??"] * (len(h) - 1))
    return h

def generate_deck(num=1): # shuffles num decks of cards and returns them
    deck = []
    for suit in {"D", "C", "H", "S"}:
        for value in {"A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"}:
            deck.append(suit + value)
    deck = deck * num
    random.shuffle(deck)
    return deck

def generate_turn(cog, hands, hand, roundnum, t, hi, wallets, add_moves = True): # embed generator for a turn given all the game info
    player = hand["player"]
    embed = botembed(f"Round {roundnum} // {player.name}'s Turn")
    handstr = ""
    strindex = 0
    for h in hands[:-1]:
        toadd = ""
        arrow = ""
        if strindex == hi: 
            toadd = "**" 
            arrow = ">"
        handstr = handstr + f"{toadd}-{arrow} <@{h['player'].id}>: `{', '.join(process_hand(h['cards']))}`{toadd}\n"
        strindex += 1
    handstr = handstr + f"Dealer (<@{cog.bot.user.id}>): `{', '.join(process_hand(hands[-1]['cards'], mask=True))}`"
    embed.add_field(name="Hands", value=handstr, inline=False)
    possible = []
    actionstr = ""
    if not hand["dd"]:
        actionstr = actionstr + "👆 HIT\n- Take another card\n"
        possible.append("👆")
    actionstr = actionstr + "👋 STAND\n- Take no more cards, ending your turn\n"
    possible.append("👋")
    if not hand["dd"]:
        if hand["bet"] <= wallets[player]:
            actionstr = actionstr + "💵 DOUBLE DOWN\n- Double your bet, and take one more card\n"
            possible.append("💵")
    if hand["splitable"]:
        if hand["bet"] <= wallets[player]:
            actionstr = actionstr + "✌️ SPLIT\n- Splits your hand into two and doubles your bet (one bet for each hand)\n"
            possible.append("✌️")
    if t == 1:
        actionstr = actionstr + "👉 SURRENDER\n- Remove yourself from play for this round, regaining half of your bet"
        possible.append("👉")
    if add_moves:
        embed.add_field(name="Actions", value=actionstr, inline=False)
    return embed, possible

values = {
    "A2": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11
}



class BlackJack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ims = {}
        self.responded = {}
        self.start = {}
        self.playing = []

        self.rounds = 10
        self.ante = 10
        self.starting = 100

    @commands.command()
    async def blackjack(self, ctx, members: commands.Greedy[discord.Member]=None):
        if members is not None: # basic invite handler
            if ctx.author.id in self.responded or ctx.author.id in self.playing:
                embed = error("🚫 " + self.bot.response(2) + " you already have a game running!")
                return await ctx.send(embed=embed)

            self.ims[ctx.author.id] = mp.InviteManager(self, self.bot, ctx, "Blackjack")
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

        hands = []
        wallets = {}
        for p in players:
            wallets[p] = self.starting
            self.playing.append(p)

        embed = botembed("Game Started")
        desc = "🃏 " + self.bot.response(1) + f" I started a game of Blackjack.\nI will be the dealer.\nAll players have been given `${self.starting}` to start.\nBlackjacks pay 3 to 2.\nDealer hands will draw to 16 and stand on all 17's.\nThe minimum bet per round is `${self.ante}`.\nThe game will go on for `{self.rounds} rounds`.\n\nThe order of play is as follows:"
        for c, player in enumerate(players):
            desc = desc + f"\n{c + 1}: <@{player.id}>"
        desc = desc + "\n\nThe game will start in 10 seconds."
        embed.description = desc
        await ctx.send(embed=embed)
        await asyncio.sleep(10)
        for roundnum in range(self.rounds):
            players = [p for p in players if wallets[p] > 0]
            if len(players) == 0: break
            roundnum += 1
            hands = []
            deck = generate_deck()
            for p in players:
                embed = botembed(f"Round {roundnum} // Betting")
                minbet = self.ante if self.ante <= wallets[p] else wallets[p]
                maxbet = wallets[p]
                embed.description = f"🃏 It is now <@{p.id}>'s turn to bet.\nYou have `${wallets[p]}` in your wallet.\nEnter an amount between {minbet} and {maxbet} to bet."
                await ctx.send(embed=embed)

                def check(message):
                    if message.channel.id == ctx.channel.id:
                        if message.author.id == p.id:
                            c = message.content.lower().strip()
                            if message.content.isdecimal():
                                val = int(c)
                                return minbet <= val <= maxbet
                    return False
                m = await self.bot.wait_for("message", check=check)
                bet = int(m.content.lower().strip())
                wallets[p] -= bet
                hand = {
                    "player": p,
                    "cards": deck[:2],
                    "split": False,
                    "bet": bet,
                    "splitable": False,
                    "dd": False
                }
                vals = set(values[x[1:]] for x in hand["cards"]) 
                if len(vals) == 1: # checks if hand is splitable
                    if list(vals)[0] != 11:
                        hand["splitable"] = True
                    else:
                        hand["cards"][1] = hand["cards"][1][0] + "A2"

                del deck[:2]
                hands.append(hand)

            bothand = { # config for the bot's hand
                    "player": self.bot.user,
                    "cards": deck[:2],
                    "split": False,
                    "bet": 0,
                    "splitable": False,
                    "dd": False
                }
            del deck[:2]
            hands.append(bothand)
            payout = players.copy()
            hi = 0
            hmax = len(hands) - 1
            while hi < hmax:
                hand = hands[hi]

                if get_value(hand["cards"]) == 21: # natural/blackjack
                    embed = botembed(f"Round {roundnum} // {player.name}'s Turn")
                    handstr = ""
                    for h in hands[:-1]:
                        handstr = handstr + f"- <@{h['player'].id}>: `{', '.join(process_hand(h['cards']))}`\n"
                    handstr = handstr + f"Dealer (<@{self.bot.user.id}>): `{', '.join(process_hand(hands[-1]['cards'], mask=True))}`"
                    embed.add_field(name="Hands", value=handstr, inline=False)
                    embed.description = "🃏 " + self.bot.response(5) + f" You got a blackjack!\n`${int(hand['bet'] // 2 * 3)}` has been added to your wallet.\nThe next player's turn will begin in 10 seconds."
                    wallets[hand["player"]] += (int(hand['bet']) // 2) * 5
                    await ctx.send(embed=embed)
                    await asyncio.sleep(10)
                    payout[hi] = "blackjack"
                    hi += 1
                    continue

                t = 1

                embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets)
                embed.description = "Select an action using the corresponding emoji."
                menu = await ctx.send(embed=embed)
                for p in possible:
                    await menu.add_reaction(p)

                t += 1
                while True:
                    def check(reaction, user):
                        if reaction.message.id == menu.id:
                            if reaction.emoji in possible:
                                if hand["player"].id == user.id:
                                    return True
                        return False

                    reaction = await self.bot.wait_for("reaction_add", check=check)
                    e = reaction[0].emoji
                    possible = []
                    if e == "👋":
                        embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets, add_moves=False)
                        embed.description = "You have decided to stand for this round.\nThe next player's turn will begin in 10 seconds."
                        await menu.edit(embed=embed)
                        await menu.clear_reactions()
                        await asyncio.sleep(10)
                        hi += 1
                        break
                    if e == "👆":
                        cards, deck, busted = hit(hand["cards"], deck)
                        hand["cards"] = cards
                        hands[hi] = hand
                        if busted:
                            embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets, add_moves=False)
                            embed.description = "You drew an additional card and busted!\nThe next player's turn will begin in 10 seconds."   
                            payout[hi] = None
                            await menu.edit(embed=embed)
                            await menu.clear_reactions()
                            await asyncio.sleep(10)
                            hi += 1
                            break
                        else:
                            embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets)
                            embed.description = "A new card has been added to your hand!\nSelect an action using the corresponding emoji."
                            await menu.edit(embed=embed)
                            
                            await menu.clear_reactions()
                            for p in possible:
                                await menu.add_reaction(p)

                            continue
                    if e == "💵":
                        cards, deck, busted = hit(hand["cards"], deck)
                        hand["cards"] = cards
                        wallets[player] -= hand["bet"]
                        hand["bet"] *= 2
                        hand["dd"] = True
                        hands[hi] = hand
                        
                        if busted:
                            embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets, add_moves=False)
                            embed.description = f"Your bet was doubled to `${hand['bet']}`.\nYou drew an additional card and busted!\nThe next player's turn will begin in 10 seconds."   
                            payout[hi] = None
                            await menu.edit(embed=embed)
                            await menu.clear_reactions()
                            await asyncio.sleep(10)
                            hi += 1
                            break
                        else:
                            embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets)
                            embed.description = f"Your bet was doubled to `${hand['bet']}`.\nA new card has been added to your hand!\nSelect an action using the corresponding emoji."
                            await menu.edit(embed=embed)
                            await menu.clear_reactions()
                            for p in possible:
                                await menu.add_reaction(p)

                            continue
                    if e == "✌️":
                        cards = hand["cards"]
                        h1c1 = cards[0]
                        h1c2 = deck[0]
                        h2c1 = cards[1]
                        h2c2 = deck[1]
                        deck = deck[2:]
                        cards[1] = h1c2
                        hands[hi] = hand 
                        hmax += 1
                        nh = {
                            "player": player,
                            "cards": [h2c1, h2c2],
                            "split": True,
                            "bet": hand["bet"],
                            "splitable": False,
                            "dd": False
                        }
                        hands.insert(hi + 1, nh)
                        payout.insert(hi + 1, player)
                        wallets[player] -= hand["bet"]
                        embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets)
                        embed.description = f"Your hand was split into two hands!\nSelect an action using the corresponding emoji."
                        await menu.edit(embed=embed)
                        await menu.clear_reactions()
                        for p in possible:
                            await menu.add_reaction(p)

                        continue
                    if e == "👉":
                        embed, possible = generate_turn(self, hands, hand, roundnum, t, hi, wallets, add_moves=False)
                        embed.description = f"You have surrendered your hand.\nHalf of your bet was returned to you.\nThe next player's turn will begin in 10 seconds."   
                        payout[hi] = None
                        wallets[player] += int(hand["bet"] // 2)
                        await menu.edit(embed=embed)
                        await menu.clear_reactions()
                        await asyncio.sleep(10)
                        hi += 1
                        break
            busted = False
            embed = botembed(f"Round {roundnum} // Round Over")
            tval = get_value(hands[-1]['cards'])
            while tval < 17:
                cards, deck, busted = hit(hands[-1]['cards'], deck)
                hands[-1]["cards"] = cards
                
                tval = get_value(cards)
                if busted:
                    break
            
            if busted:
                embed.description = "The dealer busted!\nAll remaining players won their bets.\nThe next round will begin in 10 seconds."
            else:
                embed.description = f"The dealer drew to a total of {tval}.\nAll winning players won their bets.\nThe next round will begin in 10 seconds"

            win = []
            loss = []
            tie = []
            for i, player in enumerate(payout):
                hand = hands[i]
                if player:
                    if player == "blackjack":
                        continue
                    if busted:
                        win.append(hand)
                        wallets[player] += (hand["bet"] * 2)
                    else:
                        val = get_value(hands[i]["cards"])
                        if val > tval:
                            win.append(hand)
                            wallets[player] += (hand["bet"] * 2)
                        elif val == tval:
                            tie.append(hand)
                            wallets[player] += hand["bet"]
                        else:
                            loss.append(hand)
                else:
                    loss.append(hand)
            
            handstr = ""
            for h in hands[:-1]:
                handstr = handstr + f"- <@{h['player'].id}>: `{', '.join(process_hand(h['cards']))}` ({get_value(h['cards'])})\n"
            handstr = handstr + f"Dealer (<@{self.bot.user.id}>): `{', '.join(process_hand(hands[-1]['cards']))}` ({tval})"
            embed.add_field(name="Hands", value=handstr, inline=False)
            
            payoutstr = ""
            for h in hands[:-1]:
                player = h["player"]
                if h in win:
                    payoutstr = payoutstr + f"- <@{player.id}> won their bet of `${h['bet']}` with a score of {get_value(h['cards'])}. They now have `${wallets[player]}`.\n"
                elif h in loss:
                    payoutstr = payoutstr + f"- <@{player.id}> lost their bet of `${h['bet']}` with a score of {get_value(h['cards'])}. They now have `${wallets[player]}`.\n"
                else:
                    payoutstr = payoutstr + f"- <@{player.id}> tied and regained their bet of `${h['bet']}`. They now have `${wallets[player]}`.\n"
            
            embed.add_field(name="Payouts", value=payoutstr, inline=False)
            await ctx.send(embed=embed)
            await asyncio.sleep(10)
        embed = botembed("Game Over")
        embed.description = "The game has ended!"
        w = ""
        for p in wallets:
            w = w + f"- <@{p.id}>: `${wallets[p]}`\n"
        embed.add_field(name="Final Wallets", value=w)
        await ctx.send(embed=embed)
        if ctx.author.id in self.responded: del self.responded[ctx.author.id]
        if ctx.author.id in self.responded: del self.start[ctx.author.id] # redundant but necessary for some reason?
        if ctx.author.id in self.responded: del self.ims[ctx.author.id]
        # clear game data


async def setup(bot):
    await bot.add_cog(BlackJack(bot))