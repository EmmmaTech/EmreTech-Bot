import discord
import os
import json
from discord.ext import commands

class Utility(commands.Cog):
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
        await ctx.send("Unimplemented.")

def setup(bot):
    bot.add_cog(Utility(bot))