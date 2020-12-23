import os
import discord
import json
import aiofiles
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

def fetch_prefix(bot, message):
    """Function that fetches a server's prefixes.

    Used as input to the command_prefix for commands.Bot initialization.
    Must be a module-level function, as that is the only type of function commands.Bot accepts."""

    prefixes = ["!"]

    if not message.guild:
        return "!"
    if message.guild.id in bot.prefix.prefix_dict:
        prefixes = bot.prefix.prefix_dict[message.guild.id]

    return commands.when_mentioned_or(*prefixes)(bot, message)

class PrefixCog(commands.Cog):
    """Class that handles a bot's per-server command prefix data.

    Attributes:
        data (str): path to a file containing prefix data.
        prefix_dict (dict): dict containing server ID keys and lists of prefixes as values.
        lock (asyncio.Lock): lock to protect against race conditions when saving prefix data."""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.prefix_dict = self.load_prefix(data)
        self.lock = asyncio.Lock()

    async def guild_check(self, ctx):
        """Method that checks if a message has been sent in a server, and sends an error in response if not."""
        
        if not ctx.guild:
            await ctx.send("Error: Prefixes cannot be changed in DMs, only servers.")
        return ctx.guild

    @commands.command(name="prefix", help="Lists the prefixes the server is using.")
    async def prefix(self, ctx):
        """Method that responds to a command with the prefixes the server is using."""

        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in self.prefix_dict:
                prefixes = self.prefix_dict[guild]
                await ctx.send("This server has the following custom prefixes: " + " ".join(prefixes))
            else:
                await ctx.send("This server is using the default prefix: !")

    @commands.command(name="add_prefix", help="Adds an inputted prefix to a server.")
    @commands.has_permissions(administrator=True)
    async def add_prefix(self, ctx, prefix: str):
        """Method that adds an inputted prefix to a server."""

        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild not in self.prefix_dict:
                self.prefix_dict[guild] = [prefix]
                await ctx.send("The defualt prefix ! has been replaced with the prefix: " + prefix)
            else:
                self.prefix_dict[guild].append(prefix)
                await ctx.send("This server now works with the additional prefix: " + prefix)
            await self.save_prefix(self.data)

    @commands.command(name="set_prefix", help="Sets an inputted prefix to a server.")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        """Method that sets an inputted prefix to a server."""

        if await self.guild_check(ctx):
            guild = ctx.guild.id
            self.prefix_dict[guild] = [prefix]
            await ctx.send("This server's prefix has been set to this prefix: " + prefix)
            await self.save_prefix(self.data)

    @commands.command(name="reset_prefix", help="Resets the prefix list on a server to the default.")
    @commands.has_permissions(administrator=True)
    async def reset_prefix(self, ctx):
        """Method that resets the prefix list on a server to the default."""

        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in self.prefix_dict:
                self.prefix_dict.pop(guild)
                await ctx.send("This server's prefix has been set to the default prefix: !")
                await self.save_prefix(self.data)
            else:
                await ctx.send("This server is already set to the default prefix: !")

    @commands.command(name="remove_prefix", help="Removes an inputted prefix from a server.")
    @commands.has_permissions(administrator=True)
    async def remove_prefix(self, ctx, prefix: str):
        """Method that removes an inputted prefix from a server."""

        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in self.prefix_dict:
                if prefix in self.prefix_dict[guild]:
                    self.prefix_dict[guild].remove(prefix)
                    await ctx.send("This following prefix has been removed from this server: " + prefix)
                    if self.prefix_dict[guild] in [[], ["!"]]:
                        self.prefix_dict.pop(guild)
                        await ctx.send("This server is currently set to the default prefix: !")
                    await self.save_prefix(self.data)
                else:
                    await ctx.send("The following prefix is not set for this server: " + prefix)
            else:
                await ctx.send("This server is currently set to the default prefix: !")

    def load_prefix(self, path):
        """Method that loads prefix data to the cog."""

        with open(path, "r") as f:
            data = json.load(f)
            data = {int(server_id): data[server_id] for server_id in data}
            return data

    async def save_prefix(self, path):
        """Method that saves prefix data from this cog."""

        async with self.lock:
            with open(path, "w") as f:
                f.write(json.dumps(self.prefix_dict, indent=4))
