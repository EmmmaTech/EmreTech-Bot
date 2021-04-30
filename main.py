description = """EmreTech's Helper Bot! Helps around in EmreTech's official server, and many more in the future!"""

# Rewrite based on the FlagBot Discord Bot, made by GriffinG1

# Module importion
import discord
import traceback
import os
import sys
import aiohttp
import json
import argparse
from discord.ext import commands

try:
    import config
except ModuleNotFoundError:
    if "-args" not in sys.argv:
        print("Config file is not available, and '-args' not passed. Bot cannot run. Quitting...\n")
        exit(1)
    else:
        pass

# Parse command arguments (if any)
def parse_cmd_arguments():
    parser = argparse.ArgumentParser(description="EmreTech-Bot")
    parser.add_argument("-env", "--env-args",
                        action="store_true",
                        help="Uses env (enviroment) variables instead of a config file")
    return parser

argpar, unknown = parse_cmd_arguments().parse_known_args()
env_run = argpar.env_args

if env_run:
    using_env_args = True
    using_config_file = False
    print("Using enviroment variables!")
else:
    using_env_args = False
    using_config_file = True
    print("Using the config file!")

# Discord Bot setup
status = discord.Activity(type=discord.ActivityType.watching)
if using_config_file:
    prefix = config.prefix
    if not config.beta:
        status.name = config.status
    else:
        if config.status.endswith( ('.', '!', '?', ' ') ):
            status.name = config.status + " Beta build."
        else:
            status.name = config.status + ". Beta build."
    token = config.token
elif using_env_args:
    prefix = os.getenv("PREFIX")
    if not bool(os.getenv("BETA")):
        status.name = os.getenv("STATUS")
    else:
        if os.getenv("STATUS").endswith( ('.', '!', '?', ' ') ):
            status.name = os.getenv("STATUS") + " Beta build."
        else:
            status.name = os.getenv("STATUS") + ". Beta build."
    token = os.getenv("TOKEN")

intents = discord.Intents.all()
helpCmd = commands.DefaultHelpCommand(width=200)

bot = commands.Bot(command_prefix=prefix, description=description, activity=status, intents=intents)
bot.help_command = helpCmd

bot.ready = False
if using_config_file:
    bot.is_beta = config.beta
elif using_env_args:
    bot.is_beta = bool(os.getenv("BETA"))

bot.deleted_dict = {} # For deleted messages
emretechofficialserver_id = 816810434811527198

if using_config_file:
    bot.rules_file = config.rules_file
    rules_channel = config.rules_channel
    logs_channel = config.logs_channel
    welcome_channel = config.welcome_channel
    bot_channel = config.bot_channel

    mute_role = config.mute_role
    admin_role = config.admin_role
    mod_role = config.mod_role

    bot.using_mod_forms = config.using_mod_forms
elif using_env_args:
    bot.rules_file = os.getenv("RULES_FILE")
    rules_channel = int(os.getenv("RULES_CHANNEL"))
    logs_channel = int(os.getenv("LOGS_CHANNEL"))
    welcome_channel = int(os.getenv("WELCOME_CHANNEL"))
    bot_channel = int(os.getenv("BOT_CHANNEL"))

    mute_role = int(os.getenv("MUTE_ROLE"))
    admin_role = int(os.getenv("ADMIN_ROLE"))
    mod_role = int(os.getenv("MOD_ROLE"))

    bot.using_mod_forms = bool(os.getenv("USING_MOD_FORMS"))

# Setup files
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path) # To ensure the current directory is at the project root

if not os.path.exists('saves'):
    os.mkdir('saves')

def load_from_file(fpath: str, data: dict = {}):
    if not os.path.exists(fpath):
        with open(fpath, "w") as f:
            json.dump(data, f, indent=4)
        
    with open(fpath, "r") as f:
        return json.load(f)

    print(f"File {fpath} content's have been loaded!")

bot.warns_dict = load_from_file("saves/warns.json")
bot.mutes_dict = load_from_file("saves/mutes.json")
bot.levels_dict = load_from_file("saves/levels.json")

if bot.using_mod_forms:
    bot.mod_form_answers = load_from_file("saves/mod-form-answers.json")

# Discord Bot events
@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. To get usuable commands, use `{prefix}help` to see them.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing required arguments for this command. Review the help page below:")
        await ctx.send_help(ctx.command)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad arguments were provided, try running the command again with correct arguments.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You cannot use this command due to not having the right permission.")
    else:
        if ctx.command:
            await ctx.send(f"An error occured when processing the {ctx.command.name} command. If you are a Moderator, check the bot's logs.")
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            error_trace = "".join(tb)
            print(error_trace)
            try:
                embed = discord.Embed(title=f"Error while processing {ctx.command.name} command!")
                if len(error_trace) > 512:
                    embed.description = "Error trace is too long to put here. If you have access to the Terminal running me (the bot), check there."
                else:
                    embed.description = f"```\n{error_trace}\n```"
                if bot.logs_channel is not None:
                    bot.logs_channel.send(embed=embed)
            except:
                pass

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
            if guild.id in config.whitelisted_servers:
                bot.guild = guild

                bot.rules_channel = discord.utils.get(guild.channels, id=rules_channel)
                bot.logs_channel = discord.utils.get(guild.channels, id=logs_channel)
                bot.welcome_channel = discord.utils.get(guild.channels, id=welcome_channel)
                bot.bot_channel = discord.utils.get(guild.channels, id=bot_channel)

                bot.mute_role = discord.utils.get(guild.roles, id=mute_role)
                bot.admin_role = discord.utils.get(guild.roles, id=admin_role)
                bot.moderator_role = discord.utils.get(guild.roles, id=mod_role)

                if guild.id == emretechofficialserver_id:
                    bot.protected_roles = (discord.utils.get(guild.roles, id=816810865520279565), bot.admin_role, bot.moderator_role)
            else:
                try:
                    await guild.owner.send(f"Left your server, `{guild.name}`, as under this token, this bot should only be used in ETOS (EmreTech's Official Server).")
                    await guild.owner.send('If you would like to use a bot with the same code as me, clone or fork me on [GitHub]("https://github.com/EmreTech/EmreTech-Bot").')
                except discord.Forbidden:
                    for channel in guild.channels:
                        if guild.me.permissions_in(channel).send_messages and isinstance(channel, discord.TextChannel):
                            await channel.send(f"Left your server, as under this token, this bot should only be used in ETOS (EmreTech's Official Server).")
                            await channel.send('If you would like to use a bot with the same code as me, clone or fork me on [GitHub]("https://github.com/EmreTech/EmreTech-Bot").')
                            break
                finally:
                    await guild.leave()

            try:
                with open("restart.txt", "r") as fil:
                    restart_channel = fil.readline()
                channel = await bot.fetch_channel(restart_channel)
                await channel.send("Successfully restarted!")
                os.remove("restart.txt")
            except (discord.NotFound, FileNotFoundError):
                pass
            print("Logged on and initialized on {0.name}.".format(guild))
        except Exception as e:
            print("Failed to initalize on {0.name}.".format(guild))
            traceback.print_tb(e.__traceback__)
    
    bot.ready = True

# Loading addons
cogs = [
    'addons.Events',
    'addons.Math',
    'addons.Fun',
    'addons.Utility',
    'addons.Mod',
    'addons.Levels'
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

# Commands for controlling the bot itself
@bot.command(hidden=True)
async def load(ctx: commands.Context, *, module):
    """Loads an addon. Only for moderators and higher."""
    if ctx.author == ctx.guild.owner or ctx.author == bot.admin_role or ctx.author == bot.moderator_role:
        try:
            bot.load_extension(f"addons.{module}")
        except Exception as e:
            await ctx.send(f":anger: Error while attemping to load the extension.\n```\n{type(e).__name__}: {e}\n```")
        else:
            await ctx.send(":white_check_mark: Extension successfully loaded.")
    else:
        raise commands.CheckFailure()

@bot.command(hidden=True)
async def unload(ctx: commands.Context, *, module):
    """Unloads an addon. Only for moderators and higher."""
    if ctx.author == ctx.guild.owner or ctx.author == bot.admin_role or ctx.author == bot.moderator_role:
        try:
            bot.unload_extension(f"addons.{module}")
        except Exception as e:
            await ctx.send(f":anger: Error while attemping to unload the extension.\n```\n{type(e).__name__}: {e}\n```")
        else:
            await ctx.send(":white_check_mark: Extension successfully unloaded.")
    else:
        raise commands.CheckFailure()

@bot.command(hidden=True)
async def restart(ctx: commands.Context):
    """Restarts the bot. Only for admins and higher."""
    if not ctx.author == ctx.guild.owner and not ctx.author == bot.admin_role:
        raise commands.CheckFailure()
    await ctx.send("Restarting the bot...")
    with open("restart.txt", "w") as fil:
        fil.write(str(ctx.channel.id))
    sys.exit(0)

# Running the bot
try:
    bot.run(token)
except aiohttp.ClientConnectorCertificateError:
    print("Unable to connect to discord.com due to a SSL Certificate error.")
except SystemExit:
    exit(0) # Just to prevent the SystemExit exception
# Add any suggestions for more exceptions to put here
