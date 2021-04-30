import discord
import json
import random
from .Helper import check_mute_expiry, hashes, handle_verify_msg
from datetime import datetime
from discord.ext import commands

class Events(commands.Cog):
    """
    Just some events that happen in the server (someone joined, someone left, on a message, on a deleted message).
    The someone joined event might be split from here in the future.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            mute_exp = self.bot.mutes_dict[str(member.id)]
        except KeyError:
            mute_exp = ""

        embed = discord.Embed(title="New member joined!")
        embed.description = f"{member.mention} | {member.name}#{member.discriminator}"
        embed.description += f"\n\n Welcome to {member.guild.name}! Please read the rules in order to continue into this server."

        if mute_exp != "" and not await check_mute_expiry(self.bot.mutes_dict, member):
            embed.add_field(name="Muted until ", value=mute_exp + " UTC")
            embed.description += "\nIf you tried to get unmuted by rejoining, it won't work. Nice try."
            await member.add_roles(self.bot.mute_role)

        if self.bot.welcome_channel is not None:
            await self.bot.welcome_channel.send(embed=embed)

        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try:
            mute_exp = self.bot.mutes_dict[str(member.id)]
        except KeyError:
            mute_exp = ""

        embed = discord.Embed(title="Member Left :(")
        embed.description = f"{member.mention} | {member.name}#{member.discriminator}"
        
        if mute_exp != "" and not await check_mute_expiry(self.bot.mutes_dict, member):
            embed.description += "\nThey will automatically be remuted when they join again."
        
        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Auto ban if someone pings 20+ times in one message
        if len(message.mentions) > 20:
            await message.delete()
            await message.author.ban()
            return await message.channel.send(f"{message.author} was banned for mass pinging (auto bans of mass pinging is 20+).")

        # TODO: When a user sends a message, they will gain xp. If they post another message within 1.5 minutes of the last message, they won't get any xp.

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        date_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        msg_id = message.id
        user_id = message.author.id
        channel_id = message.channel.id
        content = message.content

        self.bot.deleted_dict[str(msg_id)] = {
            "user": user_id,
            "channel": channel_id,
            "content": content,
            "date": date_time
        }

        embed = discord.Embed(title="Message deleted")
        embed.description = f"Message contents: \n```\n{content}\n```"
        embed.add_field(name="Date deleted", value=date_time + " UTC")
        embed.add_field(name="Message author", value=f"{message.author.mention} | {message.author.name}#{message.author.discriminator}")

        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Events(bot))