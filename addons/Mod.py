import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ban_person(self, ctx, member, reason):
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
            await member.send(f"You were banned from {self.bot.guild.name} for \n\n{reason}"
            f"\n\nIf you believe this is a mistake, please contact the Admins/Moderators of {ctx.guild.name}.")
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
    async def on_member_ban(self, guild, user):
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
        embed = discord.Embed(title=f"User {user} banned")
        embed.description = f"{user} was banned by {admin} for the following reason:\n\n{reason}"

        if self.bot.logs_channel is not None:
            await self.bot.logs_channel.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.has_any_role("Mods")
    async def kick(self, ctx, member: discord.Member, *, reason="No reason given."):
        """Kick a member."""
        if member == ctx.message.author:
            return await ctx.send("You cannot kick yourself for obvious reasons.")
        elif any(i for i in self.bot.protected_roles if i in member.roles):
            return await ctx.send("You cannot kick a protected user for obvious reasons.")
        else:
            try:
                await member.send(f"You were kicked from {self.bot.guild.name} for \n\n{reason}"
                f"\n\nIf you believe this is a mistake, you can rejoin the Discord Server.")
            except discord.Forbidden:
                pass
            if len(reason) > 512:
                await member.kick(reason="The reason length is too long. Please check public bot logs.")
            else:
                await member.kick(reason=reason)
            await ctx.send(f"Successfully kicked user {member}!")

    @commands.command(pass_context=True)
    @commands.has_any_role("Mods")
    async def ban(self, ctx, member: discord.User, *, reason="No reason given."):
        """Bans a member/user."""
        if not member:
            return await ctx.send("User not found. If you are sure this is a valid user, try using `banid` instead.")
        await self.ban_person(ctx, member, reason)
        
    @commands.command(pass_context=True)
    @commands.has_any_role("Mods")
    async def banid(self, ctx, member: int, *, reason="No reason given."):
        """Ban a user with their user ID.

        To get a user ID, enable developer mode and right click their profile."""
        member = await self.bot.fetch_user(member)
        if not member:
            return await ctx.send("This is not a valid discord user.")
        await self.ban_person(ctx, member, reason)

    # TODO: Add muting, unmuting, and timemuting a member.

def setup(bot):
    bot.add_cog(Moderation(bot))