import os
import discord
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import json
import asyncio
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
        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        if os.path.isfile(path):
            await ctx.send("Invalid poker name: name already exists!")
            return
        
        async with self.lock:
            with open(path, "w") as f:
                data = dict()
                data["rounds"] = 0
                data["balances"] = dict()
                json.dump(data, f)

    @commands.command(name="delete_poker")
    @check_valid_command
    async def delete_poker(self, ctx):
        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        if not os.path.isfile(path):
            await ctx.send("Invalid poker name: name does not exist!")
            return
        
        async with self.lock:
            os.remove(path)

    @commands.command(name="money")
    @check_valid_command
    async def money(self, ctx, name: str, amount: int):
        self.updates[name] = amount
            
    @commands.command(name="update_poker")
    @check_valid_command
    async def update_poker(self, ctx):
        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        async with self.lock:
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
    async def undo_poker(self, ctx):
        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        async with self.lock:
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
    async def balance(self, ctx):
        path = os.path.join(self.poker_dir, str(ctx.guild.id) + ".json")
        async with self.lock:
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
