import discord
from discord.ext import commands

class Math(commands.Cog):
    """
    Perform simple math operations.
    """

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
    async def solve(self, ctx: commands.Context, operation: str, a: int, b: int):
        """
        Calculates two numbers together.
        """
        answer = self.calculate(operation, a, b)
        await ctx.send("Your answer is {}.".format(answer))

    @commands.command(name="evaluate")
    async def expression(self, ctx: commands.Context, exp: str):
        """
        Calculates an expression using the eval function.
        """
        answer = eval(exp)
        await ctx.send("Your answer is {}.".format(answer))

def setup(bot):
    bot.add_cog(Math(bot))