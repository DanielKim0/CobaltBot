import os
import discord
import json
import aiofiles
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

class BasicCog(commands.Cog):
    """Class that handles a bot's per-cog server permissions data as well as any shared basic commands.

    Attributes:
        cog_data (str): path to a file containing set server prefixes.
        cog_dict (dict): dict containing cog names as keys and lists of server IDs as values.
        lock (asyncio.Lock): lock to protect against race conditions when saving cog permissions data."""

    def __init__(self, cog_data):
        self.cog_data = cog_data
        self.cog_dict = dict()
        self.lock = asyncio.Lock()

    @commands.command(name="add_cog", description="", aliases=[], usage="")
    @commands.has_permissions(administrator=True)
    async def add_cog(self, ctx, cog: str):
        """Wrapper method that adds a server to a cog's permissions list, allowing the server to use it.

        Args:
            cog (str): name of the cog to add."""

        if cog not in self.cog_dict:
            await ctx.send("Invalid cog name!")
        else:
            await self.cog_dict[cog].add_server(ctx)
            await self.save_cogs()

    @commands.command(name="remove_cog", description="", aliases=[], usage="")
    @commands.has_permissions(administrator=True)
    async def remove_cog(self, ctx, cog: str):
        """Wrapper method that removes a server to a cog's permissions list, disallowing the server to use it.

        Args:
            cog (str): name of the cog to remove."""

        if cog not in self.cog_dict:
            await ctx.send("Invalid cog name!")
        else:
            await self.cog_dict[cog].remove_server(ctx)
            await self.save_cogs()
    
    @commands.command(name="list_cogs", description="", aliases=[], usage="")
    @commands.has_permissions(administrator=True)
    async def list_cogs(self, ctx):
        """Method that lists all of the cogs that a server has added to its permissions list."""

        await ctx.send("Cogs: " + ", ".join(self.cog_dict.keys()))

    async def save_cogs(self):
        """Method that saves the current cog permissions list to a file."""

        cog_servers = dict()
        async with self.lock:
            with open(self.cog_data, "w") as f:
                for cog in self.cog_dict:
                    cog_servers[cog] = list(self.cog_dict[cog].added_servers)
                f.write(json.dumps(cog_servers, indent=4))

    def load_cogs(self):
        """Method that saves the current cog permissions list to a file."""

        with open(self.cog_data, "r") as f:
            data = json.load(f)
            for cog in data:
                self.cog_dict[cog].added_servers = set(data[cog])
