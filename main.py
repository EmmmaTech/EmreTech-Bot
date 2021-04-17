import discord
from discord.ext import commands

import asyncio
import random

description = """
EmreTech's Helper Bot! I help around with the server, or just chill with you!

May only be online when my owner runs my script!
More features coming soon!
"""

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('--------------------')

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}! Please read #rules.'.format(member))

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello to you or the mentioned person"""
        member = member or ctx.author
        await ctx.send('Hello {0.mention}!'.format(member))

    @commands.command(name="bye")
    async def goodbye(self, ctx, *, member: discord.Member = None):
        """Says goodbye to you or the mentioned person"""
        member = member or ctx.author
        await ctx.send('Bye {0.mention}! Have a good day!'.format(member))


bot.add_cog(Greetings(bot))


class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def calculate(self, operation: str, a: int, b: int):
        operation = operation.lower()
        if operation == "addition":
            return a + b
        elif operation == "subtraction":
            return a - b
        elif operation == "mutiplication":
            return a * b
        elif operation == "division":
            return a / b
        else:
            return "Error: Vaild operator type was not provided. Please provide a vaild operator."

    @commands.command()
    async def solve(self, ctx, operation: str, a: int, b: int):
        """Calculates numbers. Nothing much to say."""
        answer = self.calculate(operation, a, b)
        await ctx.send("Your answer is {}.".format(answer))


bot.add_cog(Math(bot))


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games_won = 0
        self.games_lost = 0

    @commands.command()
    async def guess(self, ctx):
        """Plays a classic guessing game."""
        await ctx.send('Guess a number between 1 and 10.')

        def is_correct(m):
            return m.author == ctx.author and m.content.isdigit()

        answer = random.randint(1, 10)

        try:
            guess = await self.bot.wait_for('message', check=is_correct, timeout=10.0)
        except asyncio.TimeoutError:
            return await ctx.send('Sorry, you took too long. The answer was {}.'.format(answer))
        
        if int(guess.content) == answer:
            await ctx.send('You are correct!')
            self.games_won += 1
        else:
            await ctx.send('Oops, thats wrong. The answer was {}.'.format(answer))
            self.games_lost += 1

    def compare_rockpaperscissors(self, bot_choice: str, player_choice: str):
        if player_choice == "rock" and bot_choice == "paper":
            self.games_lost += 1
            return 'I win! Paper beats rock!'
        elif player_choice == "paper" and bot_choice == "rock":
            self.games_won += 1
            return 'You win! Paper beats rock!'

        elif player_choice == "paper" and bot_choice == "scissors":
            self.games_lost += 1
            return 'I win! Scissors beat paper!'
        elif player_choice == "scissors" and bot_choice == "paper":
            self.games_won += 1
            return 'You win! Scissors beat paper!'

        elif player_choice == "scissors" and bot_choice == "rock":
            self.games_lost += 1
            return 'I win! Rock beats scissors!'
        elif player_choice == "rock" and bot_choice == "scissors":
            self.games_won += 1
            return 'You win! Rock beats scissors!'

        if player_choice == bot_choice:
            return 'Tie.'
        
    @commands.command(name='rock-paper-scissors')
    async def rock_paper_scissors(self, ctx):
        """Plays a classic game of rock paper scissors"""
        await ctx.send('Rock, Paper, Scissors, shoot!')

        def checker(m):
            return True

        choices = ["rock", "paper", "scissors"]

        bot_choice = random.choice(choices)

        print("I chose", bot_choice)

        try:
            response = await self.bot.wait_for('message', check=checker, timeout=15.0)
            player_choice = response.content
        except asyncio.TimeoutError:
            self.games_lost += 1
            return await ctx.send('Sorry, you took too long. This counts as loosing a game.')

        print("Player chose", player_choice)

        result = self.compare_rockpaperscissors(bot_choice, player_choice)

        await ctx.send('{}'.format(result))
    
    @commands.command()
    async def status(self, ctx):
        """Tells the player how many games they won/lost"""
        await ctx.send("You have won {} game(s)!".format(self.games_won))
        await ctx.send("You have lost {} game(s)... :(".format(self.games_lost))


bot.add_cog(Fun(bot))


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leave(self, ctx):
        """Leaves the server"""
        await ctx.send("I can't leave until the computer running me quits the program!")

    @commands.command()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when you or someone mentioned joined!"""
        await ctx.send('{0.name} joined in {0.joined_at}.'.format(member))

    @commands.command()
    async def send_dm(self, ctx, member: discord.Member, *, content):
        """Sends a DM to someone mentioned"""
        channel = await member.create_dm()
        await channel.send(content)

    @commands.command()
    async def send_ticket(self, ctx, member: discord.Member, *, content):
        """Sends a ticket to someone mentioned for support"""

        channel = await member.create_dm()
        await channel.send('Ticket from {}: {}'.format(ctx.author, content))
        await ctx.send("Don't worry! Help is on the way!")


bot.add_cog(Misc(bot))

bot.run('Insert token here')
