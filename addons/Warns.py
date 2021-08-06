import discord
import json
from datetime import datetime
from discord.ext import commands
from .Helper import restricted_to_bot_channel

class Warning(commands.Cog):
    """
    Adds the moderation tool of warnings. For some reason is seperate from the Mod addon.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role("Mods")
    async def warn(self, ctx: commands.Context, target: discord.Member, *, reason="No reason given."):
        """Warns a given user. Kicks at 3-5 warnings, ban at 6"""
        try:
            self.bot.warns_dict[str(target.id)]
        except KeyError:
            self.bot.warns_dict[str(target.id)] = []

        self.bot.warns_dict[str(target.id)].append(
            {
                "reason": reason,
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "warned_by": f"{ctx.author}",
            }
        )

        warns = self.bot.warns_dict[str(target.id)]
        dm_msg = f"You were warned on {ctx.guild}.\nThe reason provided was: `{reason}`.\nThis is warn #{len(warns)}."

        ban_user = False
        kick_user = False
        if len(warns) >= 6:
            dm_msg += f"\nYou were banned for this warn. If you believe this is a mistake, please contact the Admins/Moderators of {ctx.guild.name}."
            ban_user = True
            kick_user = False
        elif len(warns) >= 3:
            dm_msg += "\nYou were kicked for this warn. If you believe this is a mistake, you can rejoin the Discord Server."
            if len(warns) == 5:
                dm_msg += "\nYou will be automatically banned if you are warned again."
            ban_user = False
            kick_user = True
        elif len(warns) == 3:
            dm_msg += "You will be automatically kicked if you are warned again."
            ban_user = False
            kick_user = False

        try:
            await target.send(dm_msg)
        except discord.Forbidden:
            await ctx.send("Could not DM the target user.")

        with open("saves/warns.json", "w") as f:
            json.dump(self.bot.warns_dict, f, indent=4)

        if ban_user:
            await target.ban(reason=f"Warn #{len(warns)}", delete_message_days=0)
        elif kick_user:
            await target.kick(reason=f"Warn #{len(warns)}")

        await ctx.send(f"Warned {target}. This is warn #{len(warns)}.")

    @commands.command()
    @commands.has_any_role("Mods")
    async def delwarn(self, ctx: commands.Context, target: discord.Member, *, warn):
        """Deletes a user's warn. Accepts the warn number or warn reason"""
        try:
            warnings = len(self.bot.warns_dict[str(target.id)])
            if warnings == 0:
                return await ctx.send(f"{target} doesn't have any warnings!")
        except KeyError:
            return await ctx.send(f"{target} doesn't have any warnings!")

        if warn.isdigit() and warn not in self.bot.warns_dict[str(target.id)]:
            try:
                warn = self.bot.warns_dict[str(target.id)].pop(int(warn) - 1)
            except KeyError:
                return await ctx.send(f"{target} doesn't have a warn with that number.")
        else:
            try:
                self.bot.warns_dict[str(target.id)].remove(warn)
            except ValueError:
                return await ctx.send(f"{target} doesn't have a warn matching `{warn}`.")

        with open("saves/warns.json", "w") as f:
            json.dump(self.bot.warns_dict, f, indent=4)

        await ctx.send(f"Removed warn from {target}.")
        warns_count = len(self.bot.warns_dict[str(target.id)])
        embed = discord.Embed(title=f"Warn removed from {target}")
        embed.add_field(name="Warn Reason:", value=warn["reason"])
        embed.add_field(name="Warned By:", value=warn["warned_by"])
        embed.add_field(name="Warned On:", value=f"{warn['date']} UTC")
        embed.set_footer(text=f"{target.name} now has {warns_count} warn(s).")

        try:
            await target.send(f"Warn `{warn['reason']}` was removed on {ctx.guild}. You now have {warns_count} warn(s).")
        except discord.Forbidden:
            embed.description += "\n**Could not DM user.**"

        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.command()
    @restricted_to_bot_channel
    async def listwarns(self, ctx: commands.Context, target: discord.Member = None):
        """Allows a user to list their own warns, or a staff member to list a user's warns"""
        if not target or target == ctx.author:
            target = ctx.author
        elif target and self.bot.moderator_role not in ctx.author.roles:
            raise commands.CheckFailure()
            return
        try:
            warns = self.bot.warns_dict[str(target.id)]
        except KeyError:
            return await ctx.send(f"{target} has no warns.")
        
        embed = discord.Embed(title=f"Warns for {target}")
        count = 1
        for warn in warns:
            warn_date = warn["date"]
            embed.add_field(name=f"Warn #{count}", value=f"**Reason: {warn['reason']}**\n**Date: {warn_date}**")
            count += 1

        if count - 1 == 0:
            return await ctx.send(f"{target} has no warns.")
        embed.set_footer(text=f"Total warns: {count-1}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Mods")
    async def clearwarns(self, ctx: commands.Context, target: discord.Member):
        """Clears all of a user's warns"""
        try:
            warns = self.bot.warns_dict[str(target.id)]
            if len(warns) == 0:
                return await ctx.send(f"{target} doesn't have any warnings!")
            self.bot.warns_dict[str(target.id)] = []
        except KeyError:
            return await ctx.send(f"{target} already has no warnings.")
        await ctx.send(f"Cleared warns for {target}.")

        with open("saves/warns.json", "w") as f:
            json.dump(self.bot.warns_dict, f, indent=4)

        embed = discord.Embed(title=f"Warns for {target} cleared")
        embed.description = f"{target} | {target.id} had their warns cleared by {ctx.author}. Warns can be found below."
        count = 1
        for warn in warns:
            warn_date = warn["date"]
            embed.add_field(name=f"Warn #{count}", value=f"**Reason: {warn['reason']}**\n**Date: {warn_date}**")
            count += 1

        try:
            await target.send(f"All of your warnings were cleared on {ctx.guild}.")
        except discord.Forbidden:
            embed.description += "\n**Could not DM user.**"

        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Warning(bot))