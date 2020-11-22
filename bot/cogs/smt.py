import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import json
import difflib
import aiofiles
from tabulate import tabulate

class SMTCog(CobaltCog):
    def __init__(self, stats, fusions, fissions, names):
        super().__init__()
        self.stats = stats
        self.fusions = fusions
        self.fissions = fissions
        with open(names, "r") as f:
            self.names = json.load(f)
        print(self.names)

    async def get_demon(self, ctx, name: str):
        name = await self.nearest_spelling(ctx, name.lower(), self.names)
        if name is not None:
            name = " ".join([i.capitalize() for i in name.split()])
        return name

    async def stat_table(self, data):
        table = ""
        table += tabulate([data["stats"][1]], data["stats"][0], tablefmt="grid") + "\n"
        table += tabulate([data["resist"][1]], data["resist"][0], tablefmt="grid") + "\n"
        if "affinities" in data:
            table += tabulate([data["affinities"][1]], data["affinities"][0], tablefmt="grid") + "\n"
        skills = tabulate(data["skills"][1], data["skills"][0], tablefmt="grid")
        return "```\n" +  table[:-1] + "\n```", "```\n" + skills + "\n```"

    @commands.command(name="demon", description="", aliases=[], usage="")
    @check_valid_command
    async def get_stats(self, ctx, name: str):
        string = await self.get_demon(ctx, name)
        if string is not None:
            async with aiofiles.open(os.path.join(self.stats, string + ".json"), "r") as f:
                data = await f.read()
            data = json.loads(data)
            table, skills = await self.stat_table(data)
            await ctx.send(table)
            await ctx.send(skills)
