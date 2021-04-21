import discord
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when someone mentioned joined!"""
        await ctx.send('{0.name} joined in {0.joined_at}.'.format(member))

    @commands.command()
    async def send_dm(self, ctx, member: discord.Member, *, content):
        """Sends a DM to someone mentioned"""
        channel = await member.create_dm()
        await channel.send(content)

    @commands.command()
    async def send_ticket(self, ctx, member: discord.Member, *, content):
        """Sends a ticket to someone mentioned for support"""

        channel = await member.create_dm()
        await channel.send('Ticket from {}: {}'.format(ctx.author, content))
        await ctx.send("Don't worry! Help is on the way!")

def setup(bot):
    bot.add_cog(Misc(bot))