import discord
import os
import json
from datetime import datetime
from discord.ext import commands

class Utility(commands.Cog):
    """
    Useful utility commands like dming and sniping.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dm', 'pm'])
    async def send_dm(self, ctx: commands.Context, member: discord.User, *, content):
        """Sends a DM to someone mentioned."""
        if member == ctx.me:
            return await ctx.send("You cannot send a DM to me!")
        try:
            await member.send(embed=discord.Embed(title=f"DM sent to you by {member.name}#{member.discriminator}!", description=content))
        except discord.Forbidden:
            return await ctx.send("Failed to send DM to the user. They might have blocked me or aren't accepting DMs. 😢")

    @commands.command(aliases=['ticket'])
    async def send_ticket(self, ctx: commands.Context, member: discord.User, *, content):
        """Sends a ticket to someone mentioned for support."""

        if member == ctx.me:
            return await ctx.send("You cannot send a help ticket to me!")
        try:
            await member.send(embed=discord.Embed(title=f"Help ticket sent to you by {member.name}#{member.discriminator}!", description="Ticket Request:\n" + content))
        except discord.Forbidden:
            return await ctx.send("Failed to send the Help ticket to the user. They might have blocked me or aren't accepting DMs. 😢")
        await ctx.send("Don't worry! Help is on the way!")

    @commands.command()
    async def rules(self, ctx: commands.Context):
        """Prints out all the rules."""
        if os.path.exists("saves/rules.txt"):
            with open("saves/rules.txt", "r") as fil:
                rules = fil.read()
            await ctx.send(f"Here are the rules: \n```\n{rules}\n```")

    @commands.command()
    async def snipe(self, ctx: commands.Context):
        """Finds the latest deleted message. 
        Inspired by Mewdeko's snipe function."""
        cur_time = datetime.utcnow()
        recent_index = self.bot.deleted_dict[list(self.bot.deleted_dict.keys())[0]]
        first_elem = recent_index["date"]
        temp = abs(cur_time - datetime.strptime(first_elem, "%Y-%m-%d %H:%M:%S")).seconds

        try:
            for i in self.bot.deleted_dict.keys():
                dt_from_msg = self.bot.deleted_dict[i]["date"]
                if (abs(cur_time - datetime.strptime(dt_from_msg, "%Y-%m-%d %H:%M:%S")).seconds) < temp:
                    temp = abs(cur_time - datetime.strptime(dt_from_msg, "%Y-%m-%d %H:%M:%S")).seconds
                    recent_index = i

            embed = discord.Embed(title="Most recent deleted message")

            author = ctx.guild.get_member(int(recent_index["user"]))
            channel = ctx.guild.get_channel(int(recent_index["channel"]))

            embed.add_field(name="Author", value=f"{author.mention} | {author.name}#{author.discriminator}")
            embed.add_field(name="Channel", value=f"{channel.mention}")
            embed.add_field(name="Date deleted", value=recent_index["date"] + " UTC")
            content = recent_index["content"]
            embed.description = f"Message contents: \n```\n{content}\n```"

            await ctx.send(embed=embed)

        except (KeyError, ValueError):
            await ctx.send("You cannot snipe if there are no deleted messages!")

    @commands.command(aliases=['sab'])
    @commands.has_any_role("Mods")
    async def send_as_bot(self, ctx: commands.Context, channel: discord.TextChannel, *, content):
        """Sends a message as the bot. Restricted to mods and above."""
        if channel not in ctx.guild.channels:
            return await ctx.send(f"Channel {channel.mention} doesn't exist?")

        if len(content) > 1024:
            return await ctx.send(f"The message is too long to send. The message's length is {len(content)}.")

        await channel.send(content)

def setup(bot):
    bot.add_cog(Utility(bot))