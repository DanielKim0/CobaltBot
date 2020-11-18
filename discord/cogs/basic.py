import os
import discord
import json
import aiofiles
from dotenv import load_dotenv
from discord.ext import commands

class BasicCog(commands.Cog):
    def __init__(self, cog_data):
        self.cog_data = cog_data
        self.cog_dict = dict()

    @commands.command(name="ayaya", description="", aliases=[], usage="")
    async def ayaya(self, ctx):
        await ctx.send("ayaya")

    # # TODO below
    # @commands.command(name="help", description="", aliases=[], usage="")
    # async def help(self, pass_context=True):
    #     # Help message sent as response to message in server in the person's DMs
    #     pass

    @commands.command(name="add_cog", description="", aliases=[], usage="")
    async def add_cog(self, ctx, cog: str):
        if cog not in self.cog_dict:
            await ctx.send("Invalid cog name!")
        else:
            await self.cog_dict[cog].add_server(ctx)
            await self.save_cogs()

    @commands.command(name="remove_cog", description="", aliases=[], usage="")
    async def remove_cog(self, ctx, cog: str):
        if cog not in self.cog_dict:
            await ctx.send("Invalid cog name!")
        else:
            await self.cog_dict[cog].remove_server(ctx)
            await self.save_cogs()
    
    async def save_cogs(self):
        cog_servers = dict()
        async with aiofiles.open(self.cog_data, "w") as f:
            for cog in self.cog_dict:
                cog_servers[cog] = list(self.cog_dict[cog].added_servers)
            await f.write(json.dumps(cog_servers, indent=4))

    def load_cogs(self):
        print("Loading cog data.")
        with open(self.cog_data, "r") as f:
            data = json.load(f)
            for cog in data:
                self.cog_dict[cog].added_servers = set(data[cog])
                print(cog, self.cog_dict[cog].added_servers)
