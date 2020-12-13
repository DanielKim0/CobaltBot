import os
import discord
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import json
from tabulate import tabulate

class PokerCog(CobaltCog):
    def __init__(self, folder):
        super().__init__()
        self.poker_dir = folder
        self.updates = dict()
        self.lock = asyncio.Lock()

    # do by server instead of name
    @commands.command(name="create_poker")
    @check_valid_command
    async def create_poker(self, ctx):
        path = os.path.join(self.poker_dir, str(ctx.guild) + ".json")
        if os.path.isfile(path):
            await ctx.send("Invalid poker name: name already exists!")
            return
        
        with open(path, "r") as f:
            data = dict()
            data["rounds"] = 0
            data["balances"] = dict()
            json.dump(data, f)
        await ctx.send("")

    @commands.command(name="create_poker")
    @check_valid_command
    async def delete_poker(self, ctx):
        path = os.path.join(self.poker_dir, str(ctx.guild) + ".json")
        if not os.path.isfile(path):
            await ctx.send("Invalid poker name: name does not exist!")
            return
        os.remove(path)

    @commands.command(name="money")
    @check_valid_command
    async def money(self, ctx, name: str, amount: int):
        self.updates[name] = amount
            
    @commands.command(name="update_poker")
    @check_valid_command
    async def update_poker(self, ctx):
        async with self.lock:
            with open(str(ctx.guild) + ".json", "r+") as f:
                data = json.load(f)
                for name in data["balances"]:
                    if name not in self.updates:
                        data["balances"][name].append(data[name][-1])
                    else:
                        data["balances"][name].append(data[name][-1] + self.updates[name])
                        self.updates.pop(name)
                    
                for name in self.updates:
                    data["balances"][name] = [0] * data[rounds]
                    data["balances"][name].append(self.updates[name])
                data[rounds] += 1
                json.dump(data, f)

    @commands.command(name="undo_poker")
    @check_valid_command
    async def undo_poker(self, ctx):
        async with self.lock:
            with open(str(ctx.guild) + ".json", "r+") as f:
                data = json.load(f)
                for name in data["balances"]:
                    data["balances"][name].pop()
                    if len(data["balances"][name]) = 0:
                        data["balances"].remove(name)
                data[rounds] -= 1
                json.dump(data, f)

    @commands.command(name="balances")
    @check_valid_command
    async def balances(self, ctx):
        async with self.lock:
            with open(str(ctx.guild) + ".json", "r") as f:
                data = json.load(f)
                names = []
                balances = []
                
                for name in data["balances"]:
                    names.append(name)
                    balances.append(data["balances"][name][-1])

                message = "```\n"
                message += "Rounds played: " + str(data["rounds"]) + "\n"
                message += tabulate(names, balances, tablefmt="grid")
                message += "\n```"
                ctx.send(message)
