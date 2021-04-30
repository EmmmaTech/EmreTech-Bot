import discord
import json
from .Helper import restricted_to_level
from discord.ext import commands

class ModForms(commands.Cog):
    """
    A class that provides functions for a mod form.
    If the user gets to Level 20, they are able to apply to be a mod.
    The bot will dm questions to the person who applied. Theses questions will be from a file.
    Then, the bot will log the answers to server owner or the existing admins/mods.
    The server owner/admins/mods will review the form, and choose if they can become a mod.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @restricted_to_level(20)
    async def modform(self, ctx: commands.Context):
        if not self.bot.using_mod_forms:
            return await ctx.send("Bot manager for this server has turned off the modform feature.")

        try:
            await ctx.author.send("Unimplemented right now.")
        except discord.Forbidden:
            await ctx.send("You have me blocked or aren't accepting dms. 😢")

def setup(bot):
    bot.add_cog(ModForms(bot))