# DNI
# by some miracle this entire thing works
import discord
import functions

def botembed(name, title):
    embed = functions.embed(name + " - " + title, color=0x8f0000)
    return embed

def error(name, errormsg):
    embed = functions.error(name, errormsg)
    return embed

class InviteAccept(discord.ui.View):
    def __init__(self, *, timeout=300, manager=None, mid=None):
        super().__init__(timeout=timeout)
        self.manager = manager
        self.id = mid
        self.accepted = False
        self.answered = False

    @discord.ui.button(label="✔️ Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.edit_message()
        i = self.manager.invites[self.id]
        embed = botembed(self.manager.name, "Invite")
        embed.description = "🎮 Response sent!"
        await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = botembed(self.manager.name, "Invite")
        embed.description = "✅ You successfully accepted this invite!"
        await i.edit(embed=embed, view=None)
        self.accepted = True
        self.answered = True
        await self.manager.callback(self)


    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.edit_message()
        i = self.manager.invites[self.id]
        embed = botembed(self.manager.name, "Invite")
        embed.description = "🎮 Response sent!"
        await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = botembed(self.manager.name, "Invite")
        embed.description = "❌ You successfully declined this invite!"
        await i.edit(embed=embed, view=None)
        self.accepted = False
        self.answered = True
        await self.manager.callback(self)

    async def on_timeout(self):
        if self.answered: return
        i = self.manager.invites[self.id]
        embed = botembed(self.manager.name, "Invite")
        embed.description = "🎮 This invite has expired."
        await i.edit(embed=embed, view=None)
        self.manager.sent_to[self.id] = "❌ Timed Out"
        await self.manager.update()


class GameMenu(discord.ui.View):
    def __init__(self, *, timeout=None, manager=None, mid=None, required=0):
        super().__init__(timeout=timeout)
        self.manager = manager
        self.id = mid
        self.accepted = False
        self.answered = False
        self.required = required

    @discord.ui.button(label="✔️ Start Game", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.id:
            embed = error(self.manager.name, "🚫 " + self.manager.bot.response(2) + " you can't control the game because you didn't start it!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if len(self.manager.players) < self.required:
            embed = error(self.manager.name, "🚫 " + self.manager.bot.response(2) + f" you're missing the number of players (`{self.required}`) required for this game!")
            self.manager.game.responded[self.id] = True
            self.manager.game.start[self.id] = False
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        

        i = self.manager.m
        
        embed = botembed(self.manager.name, "Invite Menu")
        embed.description = "✅ You successfully started the game!"
        await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = botembed(self.manager.name, "Game Started")
        embed.description = "✅ The game has started!"
        await i.edit(embed=embed, view=None)
        self.accepted = False
        self.answered = True
        self.manager.game.responded[self.id] = True
        self.manager.game.start[self.id] = True


    

    @discord.ui.button(label="❌ Cancel Game", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.id:
            embed = error(self.manager.name, "🚫 " + self.manager.bot.response(2) + " you can't control the game because you didn't start it!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        #await interaction.response.edit_message()
        i = self.manager.m
        embed = botembed(self.manager.name, "Invite Menu")
        
        embed.description = "❌ You successfully canceled the game!"
        await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = botembed(self.manager.name, "Game Canceled")
        embed.description = "🎮 The game has been canceled."
        await i.edit(embed=embed, view=None)
        self.accepted = False
        self.answered = True
        self.manager.game.responded[self.id] = True
        self.manager.game.start[self.id] = False

    


class InviteManager:
    def __init__(self, game, bot, ctx, name):
        self.game = game
        self.bot = bot
        inviter = ctx.author
        self.players = [inviter.id]
        self.inviter = inviter
        self.name = name

        self.invites = {}
        self.sent_to = {}
        self.sent_to[inviter.id] = "✅ Accepted"


    async def callback(self, view):
        if view.accepted:
            self.players.append(view.id)
            self.sent_to[view.id] = "✅ Accepted"
        else:
            self.sent_to[view.id] = "❌ Declined"
        await self.update()


    async def update(self):
        embed = botembed(self.name, "Invite Menu")
        desc = f"🎮 {self.bot.response(1)} I've sent invites to the following people:"
        for u in self.sent_to:
            desc = desc + "\n" + f"- <@{u}>: `" + self.sent_to[u] + "`"
        embed.description = desc
        await self.m.edit(embed=embed)

    async def invite(self, user):
        try:
            embed = botembed(self.name, "Invite")
            self.sent_to[user.id] = "⏰ Pending..."
            await self.update()
            embed.description = f"🎮 You've been [invited]({self.m.jump_url}) to play `{self.name}` by <@{self.inviter.id}>!\nDo you want to join in?\n(This will time out after 5 minutes)"
            i = await user.send(embed=embed, view=InviteAccept(manager=self, mid=user.id))
            self.invites[user.id] = i
        except:
            self.sent_to[user.id] = "❌ Unable to invite"
            await self.update()