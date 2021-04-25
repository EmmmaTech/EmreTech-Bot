import discord
import functools
from datetime import datetime
from discord.ext import commands

def restricted_to_bot_channel(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_self = args[0]
        ctx = args[1]

        if ctx.author in (func_self.bot.protected_roles):
            pass
        elif not ctx.channel == func_self.bot.bot_channel and ctx.guild.id == 816810434811527198:
            await ctx.message.delete()
            return await ctx.send(f"{ctx.author.mention} This command can only be used in {func_self.bot.bot_channel.mention}.")
        await func(*args, **kwargs)
    return wrapper

async def check_mute_expiry(mutes_dict: dict, member: discord.User):
    if not str(member.id) in mutes_dict.keys():
        return None
    end_time = mutes_dict[str(member.id)]
    if end_time == "Indefinite":
        return True
    elif end_time == "":
        return None
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    diff = end_time - datetime.utcnow()
    return diff.total_seconds() < 0
