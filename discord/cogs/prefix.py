import os
import discord
import json
import aiofiles
from dotenv import load_dotenv
from discord.ext import commands
from cogs.base import CobaltCog

prefix_dict = dict()
def fetch_prefix(bot, message):
    prefixes = ["!"]

    if not message.guild:
        return "!"
    if message.guild.id in prefix_dict:
        prefixes = prefix_dict[message.guild.id]

    return commands.when_mentioned_or(*prefixes)(bot, message)

def load_prefix(path):
    with open(path, "r") as f:
        return json.load(f)

async def save_prefix(path, data):
    async with aiofiles.open(path, "w") as f:
        await f.write(json.dumps(data, indent=4))

class PrefixCog(CobaltCog):
    def __init__(self, data):
        super().__init__()
        self.data = data
        prefix_dict = load_prefix(data)

    async def guild_check(self, ctx):
        if not ctx.guild:
            await ctx.send("Error: Prefixes cannot be changed in DMs, only servers.")
        return ctx.guild

    @commands.command(name="prefix")
    async def prefix(self, ctx):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in prefix_dict:
                prefixes = prefix_dict[guild]
                await ctx.send("This server has the following custom prefixes: " + " ".join(prefixes))
            else:
                await ctx.send("This server is using the default prefix: !")

    @commands.command(name="add_prefix")
    async def add_prefix(self, ctx, prefix: str):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild not in prefix_dict:
                prefix_dict[guild] = [prefix]
                await ctx.send("The defualt prefix ! has been replaced with the prefix: " + prefix)
            else:
                prefix_dict[guild].append(prefix)
                await ctx.send("This server now works with the additional prefix: " + prefix)
            await save_prefix(self.data, prefix_dict)

    @commands.command(name="set_prefix")
    async def set_prefix(self, ctx, prefix: str):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            prefix_dict[guild] = [prefix]
            await ctx.send("This server's prefix has been set to this prefix: " + prefix)
            await save_prefix(self.data, prefix_dict)

    @commands.command(name="reset_prefix")
    async def reset_prefix(self, ctx):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in prefix_dict:
                prefix_dict.pop(guild)
                await ctx.send("This server's prefix has been set to the default prefix: !")
                await save_prefix(self.data, prefix_dict)
            else:
                await ctx.send("This server is already set to the default prefix: !")

    @commands.command(name="remove_prefix")
    async def remove_prefix(self, ctx, prefix: str):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in prefix_dict:
                if prefix in prefix_dict[guild]:
                    prefix_dict[guild].remove(prefix)
                    await ctx.send("This following prefix has been removed from this server: " + prefix)
                    if prefix_dict[guild] == []:
                        prefix_dict.pop(guild)
                        await ctx.send("This server is currently set to the default prefix: !")
                    await save_prefix(self.data, prefix_dict)
                else:
                    await ctx.send("The following prefix is not set for this server: " + prefix)
            else:
                await ctx.send("This server is currently set to the default prefix: !")
