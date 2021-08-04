import discord
import os
import json
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands
from .Helper import check_mute_expiry

class Moderation(commands.Cog):
    """
    Moderation tools only for mods and up. 
    """

    def __init__(self, bot):
        self.bot = bot
        self.mute_loop = bot.loop.create_task(self.check_mute_loop())

    def cog_unload(self):
        self.mute_loop.cancel()

    async def check_mute_loop(self):
        guild = self.bot.get_guild(816810434811527198) # TODO: Allow more guilds (server) support
        while not self.bot.is_closed():
            for m in self.bot.mutes_dict.keys():
                member = guild.get_member(int(m))
                if member is None:
                    continue

                is_expired = await check_mute_expiry(self.bot.mutes_dict, member)
                if (type(is_expired) == bool and not is_expired) or self.bot.mutes_dict[str(member.id)] == "":
                    continue
                await member.remove_roles(self.bot.mute_role)
                self.bot.mutes_dict[str(member.id)] = ""
                with open("saves/mutes.json", "w") as f:
                    json.dump(self.bot.mutes_dict, f, indent=4)
                await member.send(f"Your mute on {self.bot.guild} expired!")
            await asyncio.sleep(1)

    async def ban_person(self, ctx: commands.Context, member, reason):
        """
        A generic ban command used in ban commands.

        ctx = Commands.Context object
        member = discord.User object, aka the person to be banned
        reason = reason to ban
        """

        if member.id == ctx.message.author.id:
            return await ctx.send("You cannot ban yourself for obvious reasons.")
        try:
            member_guild = ctx.guild.get_member(member.id)
            if any(i for i in self.bot.protected_roles if i in member_guild.roles):
                return await ctx.send("You cannot ban a protected user for obvious reasons.")
        except AttributeError:
            pass

        try:
            #await member.send(f"You were banned from {self.bot.guild.name} for \n\n`{reason}`"
            #f"\n\nIf you believe this is a mistake, please contact the Admins/Moderators of {ctx.guild.name}.")
            await member.send(discord.Embed(title=f"You were banned from {self.bot.guild.name}", description=f"Reason:\n\n`{reason}`"))
        except discord.Forbidden:
            pass

        try:
            if len(reason) > 512:
                await ctx.guild.ban(member, delete_message_days=0, reason="The reason length is too long. Please check public bot logs.")
            else:
                await ctx.guild.ban(member, delete_message_days=0, reason=reason)
        except discord.Forbidden:
            return await ctx.send("I'm sorry, but the action could not be completed. Please manually ban or try again.")

        await ctx.send(f"Successfully banned user {member}!")

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        async for ban in guild.audit_logs(limit=20, action=discord.AuditLogAction.ban):
            if ban.target == user:
                if ban.reason:
                    reason = ban.reason
                else:
                    reason = "No reason given."
                admin = ban.user
                break
            else:
                return
        embed = discord.Embed(title=f"User banned")
        embed.add_field(name="User Banned", value=f"{user.mention} | {user.name}#{user.discriminator}")
        embed.add_field(name="Banned by", value=f"{admin.mention} | {admin.name}#{admin.discriminator}")
        embed.description = f"Reason: \n```\n{reason}\n```"

        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_any_role("Mods")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason="No reason given."):
        """Kick a member."""
        if member == ctx.message.author:
            return await ctx.send("You cannot kick yourself for obvious reasons.")
        elif any(i for i in self.bot.protected_roles if i in member.roles):
            return await ctx.send("You cannot kick a protected user for obvious reasons.")
        else:
            try:
                #await member.send(f"You were kicked from {self.bot.guild.name} for: \n\n`{reason}`"
                #f"\n\nIf you believe this is a mistake, you can rejoin the Discord Server.")
                await member.send(discord.Embed(title=f"You were kicked from {self.bot.guild.name}", description=f"Reason:\n\n`{reason}`"))
            except discord.Forbidden:
                pass
            if len(reason) > 512:
                await member.kick(reason="The reason length is too long. Please check public bot logs.")
            else:
                await member.kick(reason=reason)

            embed = discord.Embed(title=f"Member kicked")
            embed.add_field(name="Member Kicked", value=f"{member.mention} | {member.name}#{member.discriminator}")
            embed.add_field(name="Kicked by", value=f"{ctx.author.mention} | {ctx.author.name}#{ctx.author.discriminator}")
            embed.description = f"Reason: \n```\n{reason}\n```"

            if self.bot.logs_channel is not None: 
                await self.bot.logs_channel.send(embed=embed)

            await ctx.send(f"Successfully kicked user {member}!")

    @commands.command(pass_context=True)
    @commands.has_any_role("Mods")
    async def ban(self, ctx: commands.Context, member: discord.User, *, reason="No reason given."):
        """Bans a member/user."""
        if not member:
            return await ctx.send("User not found. If you are sure this is a valid user, try using `banid` instead.")
        await self.ban_person(ctx, member, reason)
        
    @commands.command(pass_context=True)
    @commands.has_any_role("Mods")
    async def banid(self, ctx: commands.Context, member: int, *, reason="No reason given."):
        """Ban a user with their user ID.

        To get a user ID, enable developer mode and right click their profile."""
        member = await self.bot.fetch_user(member)
        if not member:
            return await ctx.send("This is not a valid discord user.")
        await self.ban_person(ctx, member, reason)

    @commands.command()
    @commands.has_any_role("Mods")
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason="No reason given."):
        """Mutes a user."""
        if member == ctx.message.author:
            return await ctx.send("You cannot mute yourself for obvious reasons.")
        elif any(i for i in self.bot.protected_roles if i in member.roles):
            return await ctx.send("You cannot mute a protected user for obvious reasons.")
        elif self.bot.mute_role in member.roles:
            return await ctx.send("That member is muted already.")

        await member.add_roles(self.bot.mute_role)
        self.bot.mutes_dict[str(member.id)] = "Indefinite"
        with open("saves/mutes.json", "w") as f:
            json.dump(self.bot.mutes_dict, f, indent=4)
        
        try:
            #await member.send(f"You were muted on {self.bot.guild.name} for:\n\n`{reason}`")
            await member.send(embed=discord.Embed(title=f"You were muted on {self.bot.guild.name}", description=f"Reason:\n\n`{reason}`"))
        except discord.Forbidden:
            pass
        await ctx.send(f"Successfully muted {member}!")

    @commands.command()
    @commands.has_any_role("Mods")
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        """Unmutes a user."""
        if member == ctx.message.author or any(r for r in self.bot.protected_roles if r in member.roles):
            return await ctx.send(f"I wonder how {member.mention} got muted...")
        elif self.bot.mute_role not in member.roles:
            return await ctx.send("That member isn't muted.")

        await member.remove_roles(self.bot.mute_role)
        self.bot.mutes_dict[str(member.id)] = ""
        with open("saves/mutes.json", "w") as f:
            json.dump(self.bot.mutes_dict, f, indent=4)

        try:
            await member.send(f"You were unmuted on {self.bot.guild.name}.")
        except discord.Forbidden:
            pass
        await ctx.send(f"Successfully unmuted {member}!")

    @commands.command(name="tmute")
    @commands.has_any_role("Mods")
    async def timemute(self, ctx: commands.Context, member: discord.Member, duration, *, reason="No reason given."):
        """Timemutes a user with units s, m, h, and d."""
        if member == ctx.message.author:
            return await ctx.send("You cannot mute yourself for obvious reasons.")
        elif any(i for i in self.bot.protected_roles if i in member.roles):
            return await ctx.send("You cannot mute a protected user for obvious reasons.")
        elif self.bot.mute_role in member.roles:
            return await ctx.send("That member is muted already.")

        cur_time = datetime.utcnow()

        try:
            if int(duration[:-1]) == 0:
                return await ctx.send("You cannot mute for a time length of 0.")
            elif duration.lower().endswith("s"):
                diff = timedelta(seconds=int(duration[:-1]))
            elif duration.lower().endswith("m"):
                diff = timedelta(minutes=int(duration[:-1]))
            elif duration.lower().endswith("h"):
                diff = timedelta(hours=int(duration[:-1]))
            elif duration.lower().endswith("d"):
                diff = timedelta(days=int(duration[:-1]))
            else:
                await ctx.send("That's a invalid duration value.")
                return await ctx.send_help(ctx.command)
        except ValueError:
            await ctx.send("Wow, great job! A ValueError was caused! Try again please.")
            return await ctx.send_help(ctx.command)

        end = cur_time + diff
        end_str = end.strftime("%Y-%m-%d %H:%M:%S")
        await member.add_roles(self.bot.mute_role)
        self.bot.mutes_dict[str(member.id)] = end_str
        with open("saves/mutes.json", "w") as f:
            json.dump(self.bot.mutes_dict, f, indent=4)

        try:
            #await member.send(f"You were muted on {self.bot.guild.name} for:\n\n`{reason}`\n\nYou will be unmuted on {end_str}.")
            await member.send(embed=discord.Embed(title=f"You were muted on {self.bot.guild.name}", description=f"Reason:\n\n`{reason}`\n\nYou will be unmuted on {end_str}."))
        except discord.Forbidden:
            pass
        await ctx.send(f"Successfully muted {member} until `{end_str}` in UTC time!")


def setup(bot):
    bot.add_cog(Moderation(bot))