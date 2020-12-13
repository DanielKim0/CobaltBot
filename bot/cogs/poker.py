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

    # do by server instead of name
    @commands.command(name="create_poker")
    @check_valid_command
    async def create_poker(self, ctx, *args):
        name = str(ctx.guild)
        path = os.path.join(self.poker_dir, name + ".json")
        if os.path.isfile(path):
            await ctx.send("Invalid poker name: name already exists!")
            return
        
        with open(path, "r") as f:
            data = dict()
            for name in args:
                data[name] = {"cash": 0, "history": []}
            json.dump(data, f)
        await ctx.send("")

    @commands.command(name="create_poker")
    @check_valid_command
    async def delete_poker(self, ctx):
        name = str(ctx.guild)
        path = os.path.join(self.poker_dir, name + ".json")
        if not os.path.isfile(path):
            await ctx.send("Invalid poker name: name does not exist!")
            return
        os.remove(path)