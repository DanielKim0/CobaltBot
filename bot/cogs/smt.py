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
import functools

def check_valid_game(func):
    @functools.wraps(func)
    async def wrapper(*args):
        obj = args[0]
        ctx = args[1]
        if args[2] == "smt4a":
            args[2] = "smt4f"
        game = args[2]

        if game in obj.games:
            return await func(*args)
        else:
            await ctx.send("Invalid SMT game name!")
            return None
    return wrapper

class SMTCog(CobaltCog):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.games = [f.name for f in os.scandir(data) if f.is_dir()]
        self.names = self.get_names()

    def get_names(self):
        names = dict()
        for game in self.games:
            with open(os.path.join(self.data, game, "demon_names.json"), "r") as f:
                names[game] = json.load(f)
        return names

    async def get_demon(self, ctx, game, name: str):
        name = await self.nearest_spelling(ctx, name.lower(), self.names[game])
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
        if len(skills) > 2000:
            counter = 0
            split_skills = []
            skills = skills.split("\n")
            skills = ["\n".join(skills[8*i:min(8*(i+1)+1, len(skills))])
                        for i in range(int(len(skills) / 8))]
        else:
            skills = [skills]

        results = ["```\n" +  table[:-1] + "\n```"]
        for skill in skills:
            results.append("```\n" + skill + "\n```")
        return results

    @commands.command(name="demon", description="", aliases=[], usage="")
    @check_valid_command
    @check_valid_game
    async def get_stats(self, ctx, game: str, name: str):
        string = await self.get_demon(ctx, game, name)
        if string is not None:
            async with aiofiles.open(os.path.join(self.data, game, "demons", string + ".json"), "r") as f:
                data = await f.read()
            data = json.loads(data)
            for item in await self.stat_table(data):
                await ctx.send(item)

    @commands.command(name="fusion", description="", aliases=[], usage="")
    @check_valid_command
    @check_valid_game
    async def get_fusion(self, ctx, game: str, demon1: str, demon2: str):
        # Given 1 and 2, get X where 1 ! 2 = X
        demon1 = await self.get_demon(ctx, game, demon1)
        demon2 = await self.get_demon(ctx, game, demon2)
        if demon1 is not None and demon2 is not None:
            async with aiofiles.open(os.path.join(self.data, game, "fusions", demon1 + ".json"), "r") as f:
                data = await f.read()
            data = json.loads(data)
            if demon2 in data:
                msg = demon1 + " + " + demon2 + " -> " + data[demon2]
            else:
                msg = "Invalid fusion!"
            await ctx.send(msg)

    @commands.command(name="fission", description="", aliases=[], usage="")
    @check_valid_command
    @check_valid_game
    async def get_fission(self, ctx, game: str, demon1: str, demon2: str):
        # Given 1 and 2, get all X where 1 ! X = 2
        demon1 = await self.get_demon(ctx, game, demon1)
        demon2 = await self.get_demon(ctx, game, demon2)
        if demon1 is not None and demon2 is not None:
            async with aiofiles.open(os.path.join(self.data, game, "fusions", demon2 + ".json"), "r") as f:
                data = await f.read()
            data = json.loads(data)
            if demon1 in data:
                msg = demon1 + " + " + str(data[demon1]) + " -> " + demon2
            else:
                msg = "Invalid fusion!"
            await ctx.send(msg)
