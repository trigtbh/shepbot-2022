from discord.ext import commands
import functions
import settings

colors = {
    5: 0xfcfc03,
    10: 0xfcd303,
    15: 0xfcba03,
    20: 0xfca103,
    25: 0xf98803,
}
chars = {
    5: "⭐",
    10: "✨",
    15: "💫",
    20: "🌠",
    25: "🌟"
}

def find_highest(stars, d):
    key = None
    for k in d:
        if stars >= k:
            key = k
    return key

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db["MainDatabase"]["starboard"]

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not self.bot.enabled: return
        guild = self.bot.get_channel(settings.MAIN_CHANNEL).guild
        if payload.guild_id != guild.id: return
        if payload.emoji.name == settings.REACTION_NAME and payload.channel_id not in {settings.STARBOARD_CHANNEL, 699275401746186370}:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            target = None
            for item in self.db:
                if item["_id"] == message.id:
                    target = item["target"]
                    break
            schannel = self.bot.get_channel(settings.STARBOARD_CHANNEL)
            stars = 0
            for item in message.reactions:
                if item.emoji == settings.REACTION_NAME:
                    stars = item.count
                    break

            checkpoint = find_highest(stars, colors)
            if checkpoint is None: return

            char = chars[checkpoint]
            color = colors[checkpoint]

            embed = functions.embed(f"{char} {stars}", color=color)
            embed.set_author(name=message.author.name + "#" + str(message.author.discriminator), icon_url=message.author.avatar.url)
            embed.description = "[Jump!](" + message.jump_url + ")\n\n" + message.content
            if len(embed.description) > 1024:
                embed.description = embed.description[:1021] + "..."
            if len(message.attachments) > 0:
                embed.set_image(url=message.attachments[0].url)

            if target is None:
                t = await schannel.send(embed=embed)
                self.db.append({"_id": message.id, "target": t.id})
            else:
                m = await schannel.fetch_message(target)
                await m.edit(embed=embed)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not self.bot.enabled: return
        guild = self.bot.get_channel(settings.MAIN_CHANNEL).guild
        if payload.guild_id != guild.id: return
        if payload.emoji.name == settings.REACTION_NAME and payload.channel_id != settings.STARBOARD_CHANNEL:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            target = None
            for item in self.db:
                if item["_id"] == message.id:
                    target = item["target"]
                    break
            if target is None: return
            schannel = self.bot.get_channel(settings.STARBOARD_CHANNEL)
            m = await schannel.fetch_message(target)

            stars = 0
            for item in message.reactions:
                if item.emoji == settings.REACTION_NAME:
                    stars = item.count
                    break

            checkpoint = find_highest(stars, colors)
            if checkpoint is None: 
                item = {"_id": message.id, "target": target}
                del self.db[self.db.index(item)]
                return await m.delete()

            char = chars[checkpoint]
            color = colors[checkpoint]
            
            embed = functions.embed(f"{char} {stars}", color=color)
            embed.set_author(name=message.author.name + "#" + str(message.author.discriminator), icon_url=message.author.avatar.url)
            embed.description = "[Jump!](" + message.jump_url + ")\n\n" + message.content
            if len(embed.description) > 1024:
                embed.description = embed.description[:1021] + "..."
            if len(message.attachments) > 0:
                embed.set_image(url=message.attachments[0].url)

            await m.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        if not self.bot.enabled: return
        guild = self.bot.get_channel(settings.MAIN_CHANNEL).guild
        if payload.guild_id != guild.id: return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)    
        target = None
        for item in self.db:
            if item["_id"] == message.id:
                target = item["target"]
                break
        if target is None: return
        item = {"_id": message.id, "target": target}
        schannel = self.bot.get_channel(settings.STARBOARD_CHANNEL)
        message = await schannel.fetch_message(target)
        await message.delete()
        
        del self.db[self.db.index(item)]
    
async def setup(bot):
    await bot.add_cog(Starboard(bot))