import discord
import functools
import hashlib, hmac
import urllib.request
import urllib.parse
import json
from datetime import datetime
from discord.ext import commands

"""
Some useful utilities for other addons (cogs) of the bot.
"""

# A hash list for verification
hashes = ["sha1", "sha256", "sha512"]

def restricted_to_bot_channel(func):
    """Restricts the given function to the bot channel.
    
    Example:
    -------
    ```
    @commands.command()
    @restricted_to_bot_channel
    async def run_me_in_bot_channel(self, ctx):
        await ctx.send("Okay.")
    ```
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_self = args[0]
        ctx = args[1]

        try:
            if ctx.author in (func_self.bot.protected_roles):
                pass
            elif not ctx.channel == func_self.bot.bot_channel and ctx.guild.id == 816810434811527198:
                await ctx.message.delete()
                return await ctx.send(f"{ctx.author.mention} This command can only be used in {func_self.bot.bot_channel.mention}.")
            await func(*args, **kwargs)
        except:
            if ctx.author in (func_self.bot.protected_roles):
                await func(*args, **kwargs)
            else:
                return await ctx.send(f"{ctx.author.mention} This command can only be used in the bot channel.")
    return wrapper

def restricted_to_level(requiredLevel: int):
    """Restricts the given function to a given level.
    
    Code to accept arguments into the decorator taken from here: https://stackoverflow.com/a/30904603
    
    Example:
    -------
    ```
    @commands.command()
    @restricted_to_level(10)
    async def only_use_me_at_lvl_ten(self, ctx):
        await ctx.send("Good job reaching level 10!")
    ```
    """
    def outer(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            func_self = args[0]
            ctx = args[1]
            author_id = str(ctx.author.id)

            try:
                current_level = func_self.bot.levels_dict[author_id]["level"]
                
                if current_level < requiredLevel:
                    await ctx.send(f"Your level is too low to run this command. Requirement is {requiredLevel}.")
                else:
                    await func(*args, **kwargs)
            except KeyError:
                await ctx.send(f"Your level is too low to run this command. Requirement is {requiredLevel}.")
            
        return inner
    return outer
    

async def check_mute_expiry(mutes_dict: dict, member: discord.User):
    if not str(member.id) in mutes_dict.keys():
        return False
    end_time = mutes_dict[str(member.id)]
    if end_time == "Indefinite":
        return True
    elif end_time == "":
        return False
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    diff = end_time - datetime.utcnow()
    return diff.total_seconds() < 0

async def handle_verify_msg(author: discord.Member, user_hash: str, hash_used: str):
    """
    Handles the verify message, where the hash used is random.
    This checks if the provided hash matches the hash of their name and discriminator.
    """

    full = (author.name + "#" + author.discriminator).encode('utf8')

    env = {"string": full}
    env.update(globals())

    # A method I "came up with myself" to save codespace. I was originally going to use if-elif-else statements to do this same thing!
    our_hash = eval(f"hashlib.{hash_used}(string)", env)
    return hmac.compare_digest(our_hash.hexdigest().lower(), user_hash.lower())

def get_title_from_youtube_video(id: str):
    params = {
        "format": "json",
        "url": f"https://www.youtube.com/watch?v={id}"
    }
    query_string = urllib.parse.urlencode(params)
    url = f"https://www.youtube.com/oembed?{query_string}"

    with urllib.request.urlopen(url) as response:
        res_text = response.read()
        data = json.loads(res_text.decode())
        return data["title"]
