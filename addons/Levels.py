import discord
import json
import math
from discord.ext import commands
from .Helper import restricted_to_bot_channel

class Levels(commands.Cog):
    """
    Levels are based on the idea from the Mee6 bot. 
    Every time a user says a message, they earn xp. However, if they spam, they will not get extra xp.
    There is a limit of xp to earn to get to the next level. This expression is used to calculate the limit: 500 * ((level + 1) * 2).
    Levels are stored in a json file in local storage, where each member's xp are stored by the member's id.
    """

    def __init__(self, bot):
        self.bot = bot

    async def level_up(self, message: discord.Message, user: discord.Member):
        xp = self.bot.levels_dict[f'{user.id}']["xp"]
        lvl_start = self.bot.levels_dict[f'{user.id}']["level"]
        lvl_end = int(xp ** (1/4))
        
        if lvl_start < lvl_end:
            self.bot.levels_dict[f'{user.id}']["level"] = lvl_end
            await message.channel.send(f"Good job {user.mention}! You reached level {lvl_end}. Congrats!")
        elif lvl_start > lvl_end:
            self.bot.levels_dict[f'{user.id}']["level"] = lvl_end

    async def add_xp_base(self, user: discord.Member, amount_xp: int):
        if not f'{user.id}' in self.bot.levels_dict:
            self.bot.levels_dict[f'{user.id}'] = {}
            self.bot.levels_dict[f'{user.id}']["xp"] = 0
            self.bot.levels_dict[f'{user.id}']["level"] = 0
        
        self.bot.levels_dict[f'{user.id}']["xp"] += amount_xp

        with open("saves/levels.json", 'w') as f:
            json.dump(self.bot.levels_dict, f)

    async def remove_xp_base(self, user: discord.Member, amount_xp: int):
        if not f'{user.id}' in self.bot.levels_dict:
            self.bot.levels_dict[f'{user.id}'] = {}
            self.bot.levels_dict[f'{user.id}']["xp"] = 0
            self.bot.levels_dict[f'{user.id}']["level"] = 0
            return None

        self.bot.levels_dict[f'{user.id}']["xp"] -= amount_xp
        if self.bot.levels_dict[f'{user.id}']["xp"] < 0:
            self.bot.levels_dict[f'{user.id}']["xp"] = 0

        with open("saves/levels.json", 'w') as f:
            json.dump(self.bot.levels_dict, f)

    @commands.command()
    @commands.has_any_role("Mods")
    async def addxp(self, ctx: commands.Context, target: discord.Member, amount_xp: int):
        """Adds xp to a user. Only avaiable to mods and above."""
        await self.add_xp_base(target, amount_xp)
        await self.level_up(ctx.message, target)

    @commands.command()
    @commands.has_any_role("Mods")
    async def removexp(self, ctx: commands.Context, target: discord.Member, amount_xp: int):
        """Removes xp from a user. Only avaiable to mods and above."""
        await self.remove_xp_base(target, amount_xp)
        await self.level_up(ctx.message, target)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot == False:
            await self.add_xp_base(message.author, 2)
            await self.level_up(message, message.author)

    @commands.command()
    @restricted_to_bot_channel
    async def rank(self, ctx: commands.Context, target: discord.Member = None):
        """Shows the current xp and level of a specified member or themselves."""
        embed = discord.Embed()

        if not target:
            id = ctx.author.id
            embed.title = f"Current rank for {ctx.author}:"
        else:
            id = target.id
            embed.title = f"Current rank for {target}:"

        try:
            xp = self.bot.levels_dict[str(id)]["xp"]
            level = self.bot.levels_dict[str(id)]["level"]
        except KeyError:
            return await ctx.send("You cannot get a rank on someone who doesn't have any xp/levels stored.")

        embed.description = f"Current XP: {xp}"
        embed.description += f"\nCurrent Level: {level}"

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Levels(bot))