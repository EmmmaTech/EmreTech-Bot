import discord
import json
from datetime import datetime
from discord.ext import commands

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