import discord
import json
from discord.ext import commands

class Levels(commands.Cog):
    """
    Levels are based on the idea from the Mee6 bot. 
    Every time a user says a message, they earn xp. However, if they spam, they will not get extra xp.
    There is a limit of xp to earn to get to the next level. This limit increases until level 51, where it stays at 2500.
    Levels are stored in a json file in local storage, where each member's xp are stored by the member's id.
    """

    def __init__(self, bot):
        self.bot = bot

    def calculate_xp(self, amount_xp: int, level: int, cur_xp_limit: int):
        """
        Calculates the current amount of xp and level.
        Returns a list with the new level, xp, and xp limit.
        """

        def new_xp(current_xp: int, current_level: int, xp_limit: int):
            xp = xp_limit - current_xp
            level = current_level + 1
            return [level, xp, xp_limit]

        if level <= 10 and amount_xp >= 500:
            return new_xp(amount_xp, level, 500)
        elif level <= 20 and amount_xp >= 1000:
            return new_xp(amount_xp, level, 1000)
        elif level <= 30 and amount_xp >= 1500:
            return new_xp(amount_xp, level, 1500)
        elif level <= 40 and amount_xp >= 2000:
            return new_xp(amount_xp, level, 2000)
        elif level <= 50 and amount_xp >= 2500:
            return new_xp(amount_xp, level, 2500)
        elif level >= 51 and amount_xp >= 2500:
            return new_xp(amount_xp, level, 2500)
        else:
            return [level, amount_xp, cur_xp_limit]

    @commands.command()
    @commands.has_any_role("Mods")
    async def addxp(self, ctx: commands.Context, target: discord.Member, amount_xp: int):
        """Adds xp to a user. Only avaiable to mods and above."""
        #if target == ctx.author:
        #    return await ctx.send("You cannot give xp to yourself!")
        # Will be removed for now until fully tested out

        if amount_xp <= 0:
            return await ctx.send("You cannot add 0 or less than 0 to someone's xp! If you want to remove xp, use removexp instead.")

        current_xp = 0
        current_level = 0
        cur_xp_limit = 0

        try:
            current_xp = self.bot.levels_dict[str(target.id)][0]["xp"]
            current_level = self.bot.levels_dict[str(target.id)][0]["level"]
            cur_xp_limit = self.bot.levels_dict[str(target.id)][0]["xp_limit"]
        except KeyError:
            self.bot.levels_dict[str(target.id)] = []

        current_xp += amount_xp
        new_level_xp = self.calculate_xp(current_xp, current_level, cur_xp_limit)

        if new_level_xp[0] > current_level:
            await ctx.send(f"Good job {target.mention}! You leveled up to {new_level_xp[0]}!")

        self.bot.levels_dict[str(target.id)].clear()
        self.bot.levels_dict[str(target.id)].append(
            {
                "xp": new_level_xp[1],
                "xp_limit": new_level_xp[2],
                "level": new_level_xp[0]
            }
        )

        with open("saves/levels.json", "w") as f:
            json.dump(self.bot.levels_dict, f, indent=4)

        await ctx.send(f"Successfully gave {target} {amount_xp} xp!")

    @commands.command()
    @commands.has_any_role("Mods")
    async def removexp(self, ctx: commands.Context, target: discord.Member, amount_xp: int):
        """Removes xp from a user. Only avaiable to mods and above."""
        #if target == ctx.author:
        #    return await ctx.send("You cannot remove xp from yourself!")
        # Will be removed for now until fully tested out

        if amount_xp <= 0:
            return await ctx.send("You cannot remove 0 or less than 0 from someone's xp! If you want to add xp, use addxp instead.")

        current_xp = 0
        current_level = 0
        cur_xp_limit = 0

        try:
            current_xp = self.bot.levels_dict[str(target.id)][0]["xp"]
            current_level = self.bot.levels_dict[str(target.id)][0]["level"]
            cur_xp_limit = self.bot.levels_dict[str(target.id)][0]["xp_limit"]
        except KeyError:
            self.bot.levels_dict[str(target.id)] = []

        if current_xp <= 0 and current_level <= 0:
            return await ctx.send("You cannot remove xp from someone who has no xp.")

        current_xp -= amount_xp
        new_level_xp = self.calculate_xp(current_xp, current_level, cur_xp_limit)

        self.bot.levels_dict[str(target.id)].clear()
        self.bot.levels_dict[str(target.id)].append(
            {
                "xp": new_level_xp[1],
                "xp_limit": new_level_xp[2],
                "level": new_level_xp[0]
            }
        )

        with open("saves/levels.json", "w") as f:
            json.dump(self.bot.levels_dict, f, indent=4)

        await ctx.send(f"Successfully removed {target} {amount_xp} xp!")

    @commands.command()
    async def rank(self, ctx: commands.Context, target: discord.Member = None):
        embed = discord.Embed()

        if not target:
            id = ctx.author.id
            embed.title = f"Current rank for {ctx.author}:"
        else:
            id = target.id
            embed.title = f"Current rank for {target}:"

        try:
            xp = self.bot.levels_dict[str(id)][0]["xp"]
            level = self.bot.levels_dict[str(id)][0]["level"]
            xp_limit = self.bot.levels_dict[str(id)][0]["xp_limit"]
        except KeyError:
            self.bot.levels_dict[str(target.id)] = []
            return await ctx.send("You cannot get a rank on someone who doesn't have any xp/levels stored.")

        embed.description = f"Current XP: {xp}/{xp_limit}"
        embed.description += f"\nCurrent Level: {level}"

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Levels(bot))