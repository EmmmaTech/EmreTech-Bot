description = """EmreTech's Helper Bot! Helps around in EmreTech's official server, and many more in the future!"""

# Rewrite inspired by FlagBot Discord Bot, made by GriffinG1

import discord
import traceback
import sys
import aiohttp
from discord.ext import commands

try:
    import config
except ModuleNotFoundError:
    print("Config file is not available. This bot requires a config file to configure the bot properly.\n", 
    "Cannot run bot in this state. Quitting...")
    exit(1)

prefix = config.prefix
status = discord.Activity(name=config.status, type=discord.ActivityType.watching)
token = config.token

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, description=description, activity=status, intents=intents)

bot.ready = False
bot.is_beta = config.beta
emretechofficialserver_id = 816810434811527198

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing required arguments for this command. Review the help page below:")
        await ctx.send_help(ctx.command)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument was provided, try running the command again.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You cannot use this command due to not having the right permission.")
    else:
        if ctx.command:
            await ctx.send("Some error occured when processing the {0.command.name} command. Please try again.".format(ctx))

@bot.event
async def on_error(event_method, *args, **kwargs):
    if isinstance(args[0], commands.CommandNotFound):
        return
    tb = traceback.format_exc()
    error_trace = "".join(tb)
    print(error_trace)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        try:
            if guild.id == emretechofficialserver_id:
                bot.guild = guild
                bot.logs_channel = discord.utils.get(guild.channels, id=816829037896269824)
                bot.bot_channel = discord.utils.get(guild.channels, id=816831538926190662)
                bot.admin_role = discord.utils.get(guild.roles, id=816811491550429224)
                bot.moderator_role = discord.utils.get(guild.roles, id=816811731997163580)
                bot.mute_role = discord.utils.get(guild.roles, id=834471539314393109)
                bot.protected_roles = (discord.utils.get(guild.roles, id=816810865520279565), bot.admin_role, bot.moderator_role)
            print("Logged on and initialized on {0.name}.".format(guild))
        except Exception as e:
            print("Failed to initalize on {0.name}.".format(guild))
            traceback.print_tb(e.__traceback__)
    
    bot.ready = True


cogs = [
    'addons.Events',
    'addons.Math',
    'addons.Fun',
    'addons.Misc',
    'addons.Mod',
]

failed_cogs = []

for exten in cogs:
    try:
        bot.load_extension(exten)
    except Exception as e:
        print("{} failed to load. It will be ignored.".format(exten))
        failed_cogs.append([exten, type(e).__name__, e])

if not failed_cogs:
    print("All addons were loaded successfully!")

try:
    bot.run(token)
except aiohttp.ClientConnectorCertificateError:
    print("Unable to connect to discord.com due to a SSL Certificate error.")
# Add any suggestions for more exceptions to put here
