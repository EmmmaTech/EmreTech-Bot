import discord
from addons.Helper import check_mute_expiry
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            mute_exp = self.bot.mutes_dict[str(member.id)]
        except KeyError:
            mute_exp = ""

        embed = discord.Embed(title="New member joined!")
        embed.description = f"{member.mention} | {member.name}#{member.discriminator}"
        embed.description += f"\n\n Welcome to {member.guild.name}! Please read the rules in order to continue into this server."

        if mute_exp != "" and not await check_mute_expiry(self.bot.mutes_dict, member):
            embed.add_field(name="Muted until", value=mute_exp + " UTC")
            embed.description += "\nIf you tried to get unmuted by rejoining, it won't work. Nice try."
            await member.add_roles(self.bot.mute_role)

        if self.bot.welcome_channel is not None:
            await self.bot.welcome_channel.send(embed=embed)

        elif self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            mute_exp = self.bot.mutes_dict[str(member.id)]
        except KeyError:
            mute_exp = ""

        embed = discord.Embed(title="Member Left :(")
        embed.description = f"{member.mention} | {member.name}#{member.discriminator}"
        
        if mute_exp != "" and not await check_mute_expiry(self.bot.mutes_dict, member):
            embed.description += f"\nThey will automatically be remuted when they join again."
        
        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Auto ban if someone pings 20+ times in one message
        if len(message.mentions) > 20:
            await message.delete()
            await message.author.ban()
            return await message.channel.send(f"{message.author} was banned for mass pinging (auto bans of mass pinging is 20+).")

        # TODO: When a user sends a message, they will gain xp. If they post another message within 1.5 minutes of the last message, they won't get any xp.


def setup(bot):
    bot.add_cog(Events(bot))