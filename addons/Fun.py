import discord
from discord.ext import commands

import asyncio
import random

class Fun(commands.Cog):
    """
    Some fun games for people to play! More are coming soon!
    """

    def __init__(self, bot):
        self.bot = bot
        self.games_won = 0
        self.games_lost = 0

    @commands.command()
    async def guess(self, ctx: commands.Context):
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
    async def rock_paper_scissors(self, ctx: commands.Context):
        """Plays a classic game of rock paper scissors"""
        await ctx.send('Rock, Paper, Scissors, shoot!')

        def checker(m):
            return True

        choices = ["rock", "paper", "scissors"]

        bot_choice = random.choice(choices)

        print("I chose", bot_choice)

        try:
            response = await self.bot.wait_for('message', check=checker, timeout=15.0)
            player_choice = response.content.lower()
        except asyncio.TimeoutError:
            self.games_lost += 1
            return await ctx.send('Sorry, you took too long. This counts as loosing a game.')

        print("Player chose", player_choice)

        result = self.compare_rockpaperscissors(bot_choice, player_choice)

        await ctx.send('{}'.format(result))
    
    @commands.command(aliases=['dice', 'roll-dice'])
    async def roll(self, ctx: commands.Context):
        """Rolls a dice. Nothing else."""
        num = random.randint(0, 6)
        await ctx.send(f"You rolled {num}!")

    @commands.command(ailases=['coin', 'flip-coin'])
    async def flip(self, ctx: commands.Context):
        """Flips a coin. Nothing else."""
        num = int(round(random.random()))

        if num == 0:
            side = "Heads"
        else:
            side = "Tails"

        await ctx.send(f"You fliped {side}!")


    @commands.command()
    async def status(self, ctx: commands.Context):
        """Tells the player how many games they won/lost"""
        await ctx.send("You have won {} game(s)!".format(self.games_won))
        await ctx.send("You have lost {} game(s)... :(".format(self.games_lost))

def setup(bot):
    bot.add_cog(Fun(bot))