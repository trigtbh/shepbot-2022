import discord
from discord.ext import commands
import settings

import os
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

import functions

class AuditLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.get_channel(settings.LOG_CHANNEL)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not self.bot.enabled: return
        if channel.guild.id != self.log.guild.id:
            return
        embed = functions.embed("**Channel created**", 0x23d160)
        embed.description = f"**<#{channel.id}>** was created."
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not self.bot.enabled: return
        if channel.guild.id != self.log.guild.id:
            return
        embed = functions.embed("**Channel deleted**", 0xff3700)
        embed.description = f"**{channel.name}** was deleted."
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if not self.bot.enabled: return
        if payload.guild_id != self.log.guild.id:
            return
        log = self.bot.get_channel(settings.LOG_CHANNEL)
        if not payload.cached_message:
            embed = functions.embed("**Message deleted**", 0xff3700)
            embed.description = f"Message deleted in **<#{payload.channel_id}>**.\nID: {payload.message_id}"
            embed.add_field(name="Content", value="(Message content not available)")
            await log.send(embed=embed)
        else:
            message = payload.cached_message
            embed = functions.embed("**Message deleted**", 0xff3700)
            embed.description = f"Message sent by **<@{message.author.id}>** deleted in **<#{message.channel.id}>**."
            if message.content != "":
                embed.add_field(name="Content", value=message.content)
            if len(message.attachments) != 0:
                for a in message.attachments:
                    await a.save(os.path.join(base, "assets", "auditlog", str(message.id) + "-" + a.filename))

            await log.send(embed=embed)
            if len(message.attachments) != 0:
                for a in message.attachments:
                    try:
                        await log.send("File from deleted message with ID `" + str(message.id) + "`", file=discord.File(os.path.join(base, "assets", "auditlog", str(message.id) + "-" + a.filename)))
                    except:
                        await log.send("Error sending file from deleted message with ID `" + str(message.id) + "`\nFile too large to send: " + a.filename)
                    finally:
                        os.remove(os.path.join(base, "assets", "auditlog", str(message.id) + "-" + a.filename))

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        if not self.bot.enabled: return
        if payload.guild_id != self.log.guild.id:
            return
        embed = functions.embed("**Bulk message delete**", 0xff3700)
        embed.description = f"{len(payload.message_ids)} messages deleted in **<#{payload.channel_id}>**."
        await self.log.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not self.bot.enabled: return
        if before.guild.id != self.log.guild.id:
            return
        if before.content == after.content:
            return
        embed = functions.embed("**Message edited**", 0xffff00)
        embed.description = f"[Message]({before.jump_url}) sent by **<@{before.author.id}>** edited in **<#{before.channel.id}>**."
        embed.add_field(name="Before", value=before.content)
        embed.add_field(name="After", value=after.content)
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not self.bot.enabled: return
        if guild.id != self.log.guild.id:
            return
        embed = functions.embed("**Member banned**", 0xff3700)
        good = False
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
            if entry.target == user:
                embed.description = f"**<@{user.id}>** was banned by **<@{entry.user.id}>**."
                embed.add_field(name="Reason", value=entry.reason)
                good = True
                break
        if not good:
            embed.description = f"**<@{user.id}>** was banned."
        await self.log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if not self.bot.enabled: return
        if guild.id != self.log.guild.id:
            return
        embed = functions.embed("**Member unbanned**", 0x23d160)
        good = False
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.unban):
            if entry.target == user:
                embed.description = f"**<@{user.id}>** was unbanned by **<@{entry.user.id}>**."
                embed.add_field(name="Reason", value=entry.reason)
                good = True
                break
        if not good:
            embed.description = f"**<@{user.id}>** was unbanned."
        await self.log.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.bot.enabled: return
        if member.guild.id != self.log.guild.id:
            return
        if before.channel == after.channel:
            if after.mute and not before.mute:
                async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target == member:
                        embed = functions.embed("**Member muted**", 0xff3700)
                        embed.description = f"**<@{member.id}>** was muted by **<@{entry.user.id}>**."
                        await self.log.send(embed=embed)
                        return
            elif before.mute and not after.mute:
                async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target == member:
                        embed = functions.embed("**Member unmuted**", 0x23d160)
                        embed.description = f"**<@{member.id}>** was unmuted by **<@{entry.user.id}>**."
                        await self.log.send(embed=embed)
                        return
            elif after.deaf and not before.deaf:
                async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target == member:
                        embed = functions.embed("**Member deafened**", 0xff3700)
                        embed.description = f"**<@{member.id}>** was deafened by **<@{entry.user.id}>**."
                        await self.log.send(embed=embed)
                        return
            elif before.deaf and not after.deaf:
                async for entry in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target == member:
                        embed = functions.embed("**Member undeafened**", 0x23d160)
                        embed.description = f"**<@{member.id}>** was undeafened by **<@{entry.user.id}>**."
                        await self.log.send(embed=embed)
                        return
        else:
            if before.channel is None:
                embed = functions.embed("**Member joined voice channel**", 0x23d160)
                embed.description = f"**<@{member.id}>** joined **{after.channel.name}**."
                await self.log.send(embed=embed)
            elif after.channel is None:
                embed = functions.embed("**Member left voice channel**", 0xff3700)
                embed.description = f"**<@{member.id}>** left **{before.channel.name}**."
                await self.log.send(embed=embed)
            else:
                embed = functions.embed("**Member switched voice channels**", 0xffff00)
                embed.description = f"**<@{member.id}>** switched from **{before.channel.name}** to **{after.channel.name}**."
                await self.log.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AuditLog(bot))