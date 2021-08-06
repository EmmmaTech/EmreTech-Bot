import discord
from discord.ext import commands
from .Helper import handle_verify_msg, hashes

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verify(self, ctx: commands.Context, *, user_hash: str):
        """Verifies new members. Do not use if you are already verified."""
        if not ctx.channel == self.bot.verify_channel and ctx.guild.id == 816810434811527198:
            return await ctx.send(f"{ctx.author.mention} This command can only be used in {self.bot.verify_channel.mention}.")
        if self.bot.verified_roles in ctx.author.roles:
            return await ctx.send("You have already been verified.")
        
        verified = await handle_verify_msg(ctx.author, user_hash, hashes[0])
        print(f"Hash is legit: {verified}")
        
        if not verified:
            await ctx.send("Invalid. Please try again.")
            return await ctx.send(f"Use the {hashes[0]} hashing method to hash your full username. Use !verify [your hash here] to verify yourself.")

        await ctx.send("You have been verified!")
        await ctx.author.add_roles(self.bot.verified_roles)

def setup(bot):
    bot.add_cog(Verify(bot))