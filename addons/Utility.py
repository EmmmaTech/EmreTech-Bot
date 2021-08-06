import discord
import os
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
from discord.ext import commands
from .Helper import get_title_from_youtube_video

class Utility(commands.Cog):
    """
    Useful utility commands like dming and sniping.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dm', 'pm'])
    async def send_dm(self, ctx: commands.Context, member: discord.User, *, content):
        """Sends a DM to someone mentioned."""
        if member == ctx.me:
            return await ctx.send("You cannot send a DM to me!")
        try:
            await member.send(embed=discord.Embed(title=f"DM sent to you by {ctx.author.name}#{ctx.author.discriminator}!", description=content))
        except discord.Forbidden:
            return await ctx.send("Failed to send DM to the user. They might have blocked me or aren't accepting DMs. 😢")

    @commands.command(aliases=['ticket'])
    async def send_ticket(self, ctx: commands.Context, member: discord.User, *, content):
        """Sends a ticket to someone mentioned for support."""

        if member == ctx.me:
            return await ctx.send("You cannot send a help ticket to me!")
        try:
            await member.send(embed=discord.Embed(title=f"Help ticket sent to you by {ctx.author.name}#{ctx.author.discriminator}!", description="Ticket Request:\n" + content))
        except discord.Forbidden:
            return await ctx.send("Failed to send the Help ticket to the user. They might have blocked me or aren't accepting DMs. 😢")
        await ctx.send("Don't worry! Help is on the way!")

    @commands.command()
    async def snipe(self, ctx: commands.Context):
        """Finds the latest deleted message. 
        Inspired by Mewdeko's snipe function."""
        try:
            cur_time = datetime.utcnow()
            recent_index = self.bot.deleted_dict[list(self.bot.deleted_dict.keys())[0]]
            first_elem = recent_index["date"]
            temp = abs(cur_time - datetime.strptime(first_elem, "%Y-%m-%d %H:%M:%S")).seconds

            for i in self.bot.deleted_dict.keys():
                dt_from_msg = self.bot.deleted_dict[i]["date"]
                if (abs(cur_time - datetime.strptime(dt_from_msg, "%Y-%m-%d %H:%M:%S")).seconds) < temp:
                    temp = abs(cur_time - datetime.strptime(dt_from_msg, "%Y-%m-%d %H:%M:%S")).seconds
                    recent_index = i

            embed = discord.Embed(title="Most recent deleted message")

            author = ctx.guild.get_member(int(recent_index["user"]))
            channel = ctx.guild.get_channel(int(recent_index["channel"]))

            embed.add_field(name="Author", value=f"{author.mention} | {author.name}#{author.discriminator}")
            embed.add_field(name="Channel", value=f"{channel.mention}")
            embed.add_field(name="Date deleted", value=recent_index["date"] + " UTC")
            content = recent_index["content"]
            embed.description = f"Message contents: \n```\n{content}\n```"

            await ctx.send(embed=embed)
        except (KeyError, ValueError, IndexError):
            await ctx.send("You cannot snipe if there are no deleted messages!")

    @commands.command(aliases=['sab'])
    @commands.has_any_role("Mods")
    async def send_as_bot(self, ctx: commands.Context, channel: discord.TextChannel, *, content):
        """Sends a message as the bot. Restricted to mods and above."""
        if channel not in ctx.guild.channels:
            return await ctx.send(f"Channel {channel.mention} doesn't exist?")

        if len(content) > 1024:
            return await ctx.send(f"The message is too long to send. The message's length is {len(content)}.")

        await channel.send(content)

    @commands.command(aliases=['yt', 'search'])
    async def search_yt(self, ctx: commands.Context, searchRes: str, videoNum: int = -1):
        """Searchs for a YouTube video."""
        # Spaces and some other characters aren't allowed in url links. They are encoded with urllib.
        encoded_search_res = urllib.parse.quote(searchRes)
        htm = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={encoded_search_res}")
        video_id = re.findall(r"watch\?v=(\S{11})", htm.read().decode())

        if videoNum > -1:
            try:
                await ctx.send(f"https://www.youtube.com/watch?v={video_id[videoNum]}")
            except KeyError:
                await ctx.send(f"Error: video at {videoNum} index doesn't exist.")
        else:
            embed = discord.Embed()
            embed.title = f"Search results for {searchRes} (goes up to 20 videos)"
            embed.description = "```\n"

            itr = len(video_id)
            if itr > 20: itr = 20

            for i in range(itr):
                embed.description += f"{i}: {get_title_from_youtube_video(video_id[i])}\n"

            embed.description += "```"
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Mods")
    async def purge(self, ctx: commands.Context, numOfMessages: int, silent: bool = False):
        """Purges a bulk of messages all at once. Restricted to mods and above."""
        if numOfMessages < 1:
            return await ctx.send("The amount of messages to delete is lower than 1!")
        elif numOfMessages > 99:
            return await ctx.send("The amount of messages to delete is greater than 99!")

        def check(m):
            return True

        deleted = await ctx.channel.purge(limit=numOfMessages+1, check=check, bulk=True)
        if not silent:
            await ctx.send(f"Successfully deleted {len(deleted)} message(s)!")

def setup(bot):
    bot.add_cog(Utility(bot))