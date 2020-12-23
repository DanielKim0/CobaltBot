import os
import discord
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import json
import asyncio
from tabulate import tabulate
import functools

def check_created_game(arg):
    """Decorator that checks if a game has been created for a particular server.

    Needs to be a module-level function because decorators don't recognize self at class definition 
    time, so I have to pass the self object indirectly through the inputted function instead.
    The internal decorator is used to allow the external decorator to pass in an argument.
    
    Args:
        arg (bool): whether the poker game should exist or not.

    Returns:
        function: the inputted function wrapped by functools if command is valid, else None."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            obj = args[0]
            ctx = args[1]
            if (str(ctx.guild.id) in obj.locks) == arg:
                return await func(*args)
            else:
                if not arg:
                    await ctx.send("Error: poker game already exists!")
                else:
                    await ctx.send("Error: poker game does not exist!")
                return None
        return wrapper
    return decorator

class PokerCog(CobaltCog):
    """Cog that handles poker game statistic functionality.

    Attributes:
        poker_dir (str): path to a folder containing files with player amount data.
        updates (dict): a dictionary of amount updates to be added to player totals.
        locks (dict): a dictionary of locks, one per server ID.
    """

    def __init__(self, folder):
        super().__init__()
        self.poker_dir = folder
        self.updates = dict()
        self.locks = self.make_locks()

    def make_locks(self):
        """Method that makes the lock dictionary from existing games."""

        locks = dict()
        for name in os.listdir(self.poker_dir):
            name = os.path.splitext(os.path.basename(name))[0]
            locks[name] = asyncio.Lock()
        return locks

    # do by server instead of name
    @commands.command(name="create_poker")
    @check_valid_command
    @check_created_game(False)
    async def create_poker(self, ctx):
        """Method that creates a poker game in a server."""
        
        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        if os.path.isfile(path):
            await ctx.send("Invalid poker name: name already exists!")
            return
        
        async with self.locks[str(ctx.guild.id)]:
            with open(path, "w") as f:
                data = dict()
                data["rounds"] = 0
                data["balances"] = dict()
                json.dump(data, f)

    @commands.command(name="delete_poker")
    @check_valid_command
    @check_created_game(True)
    async def delete_poker(self, ctx):
        """Method that removes a poker game in a server."""

        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        if not os.path.isfile(path):
            await ctx.send("Invalid poker name: name does not exist!")
            return
        
        async with self.locks[str(ctx.guild.id)]:
            os.remove(path)

    @commands.command(name="money")
    @check_valid_command
    @check_created_game(True)
    async def money(self, ctx, name: str, amount: int):
        """Method that updates a player's monetary total by an amount."""

        self.updates[name] = amount
            
    @commands.command(name="update_poker")
    @check_valid_command
    @check_created_game(True)
    async def update_poker(self, ctx):
        """Method that updates a server's money totals."""

        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        async with self.locks[str(ctx.guild.id)]:
            with open(path, "r") as f:
                data = json.load(f)

            with open(path, "w") as f:
                for name in data["balances"]:
                    if name not in self.updates:
                        data["balances"][name].append(data["balances"][name][-1])
                    else:
                        data["balances"][name].append(data["balances"][name][-1] + self.updates[name])
                        self.updates.pop(name)
                    
                for name in self.updates:
                    data["balances"][name] = [0] * data["rounds"]
                    data["balances"][name].append(self.updates[name])
                data["rounds"] += 1
                json.dump(data, f)

    @commands.command(name="undo_poker")
    @check_valid_command
    @check_created_game(True)
    async def undo_poker(self, ctx):
        """Method that undos the most recent edit to a server's poker amounts."""

        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        async with self.locks[str(ctx.guild.id)]:
            with open(path, "r") as f:
                data = json.load(f)
                
            with open(path, "w") as f:
                for name in data["balances"]:
                    data["balances"][name].pop()
                for name in list(data["balances"]):
                    if len(data["balances"][name]) == 0 or all(i == 0 for i in data["balances"][name]):
                        data["balances"].pop(name)
                data["rounds"] -= 1
                json.dump(data, f)

    @commands.command(name="balance")
    @check_valid_command
    @check_created_game(True)
    async def balance(self, ctx):
        """Method that fetches and displays a server's current poker balance."""

        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        async with self.locks[str(ctx.guild.id)]:
            with open(path, "r") as f:
                data = json.load(f)
                names = []
                balances = []
                
                for name in data["balances"]:
                    names.append(name)
                    balances.append(data["balances"][name][-1])

                message = "```\n"
                message += "Rounds played: " + str(data["rounds"]) + "\n"
                message += tabulate([names, balances], tablefmt="grid")
                message += "\n```"
                await ctx.send(message)
