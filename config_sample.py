# Inspired by FlagBot's configuration file.

token  = "" # Bot's token (required to run, check discord.py's documentation for more information on running a bot)
prefix = "!" # A prefix to call bot commands with. By default it is set to '!'
status = "anyone who uses the prefix {} in a command.".format(prefix) # Status message for the bot. Defaults to the current set value. If the bot is a beta build, an additonal "Beta Build." part will be added.
beta   = False # Used to determine if the bot is a beta build or release build.

whitelisted_servers = [816810434811527198] # Whitelisted servers that the bot can only join. The id already in there is the id for EmreTech's Official Server, you can delete it.

rules_file      = "saves/rules.txt" # Rules file for the bot to resend the rules in a rules channel.
rules_channel   = 000000000000000000 # Rules channel. See above.
logs_channel    = 000000000000000000 # Logs channel for logging moderator stuff.
welcome_channel = 000000000000000000 # Welcome channel for sending welcome messages.
bot_channel     = 000000000000000000 # Bot channel for requiring certain commands inside of it only.

mute_role  = 000000000000000000 # Mute role for muting/unmuting a user.
admin_role = 000000000000000000 # Admin role
mod_role   = 000000000000000000 # Moderator role

using_mod_forms = True

# This is all the configuration that I added. You can, of course, add more configuration here.
# If in use in a real project, rename config_sample.py to config.py and configure the bot to your liking.