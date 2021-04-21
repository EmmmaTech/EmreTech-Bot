import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # TODO: Add a method to remute a user if they left and joined while still being muted

        embed = discord.Embed(title="New member joined!")
        embed.description = f"{member.mention} | {member.name}#{member.discriminator}"
        embed.description += f"\n\n Welcome to {member.guild.name}! Please read the rules in order to continue into this server."
        embed.description += "\nPlease do not reply to this message, since it is pointless."

        if self.bot.welcome_channel is not None:
            await self.bot.welcome_channel.send(embed=embed)

        elif self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title="Member Left :(")
        embed.description = f"{member.mention} | {member.name}#{member.discriminator}"
        # TODO: When mutes are implemented, there will be an additonal message that they will be remuted
        
        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
    print()