import os
import discord
import json
import aiofiles
from dotenv import load_dotenv
from discord.ext import commands

def fetch_prefix(bot, message):
    prefixes = ["!"]

    if not message.guild:
        return "!"
    if message.guild.id in bot.prefix.prefix_dict:
        prefixes = bot.prefix.prefix_dict[message.guild.id]

    return commands.when_mentioned_or(*prefixes)(bot, message)

class PrefixCog(commands.Cog):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.prefix_dict = self.load_prefix(data)

    async def guild_check(self, ctx):
        if not ctx.guild:
            await ctx.send("Error: Prefixes cannot be changed in DMs, only servers.")
        return ctx.guild

    @commands.command(name="prefix")
    async def prefix(self, ctx):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in self.prefix_dict:
                prefixes = self.prefix_dict[guild]
                await ctx.send("This server has the following custom prefixes: " + " ".join(prefixes))
            else:
                await ctx.send("This server is using the default prefix: !")

    @commands.command(name="add_prefix")
    @commands.has_permissions(administrator=True)
    async def add_prefix(self, ctx, prefix: str):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild not in self.prefix_dict:
                self.prefix_dict[guild] = [prefix]
                await ctx.send("The defualt prefix ! has been replaced with the prefix: " + prefix)
            else:
                self.prefix_dict[guild].append(prefix)
                await ctx.send("This server now works with the additional prefix: " + prefix)
            await self.save_prefix(self.data)

    @commands.command(name="set_prefix")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            self.prefix_dict[guild] = [prefix]
            await ctx.send("This server's prefix has been set to this prefix: " + prefix)
            await self.save_prefix(self.data)

    @commands.command(name="reset_prefix")
    @commands.has_permissions(administrator=True)
    async def reset_prefix(self, ctx):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in self.prefix_dict:
                self.prefix_dict.pop(guild)
                await ctx.send("This server's prefix has been set to the default prefix: !")
                await self.save_prefix(self.data)
            else:
                await ctx.send("This server is already set to the default prefix: !")

    @commands.command(name="remove_prefix")
    @commands.has_permissions(administrator=True)
    async def remove_prefix(self, ctx, prefix: str):
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
        with open(path, "r") as f:
            data = json.load(f)
            data = {int(server_id): data[server_id] for server_id in data}
            return data

    async def save_prefix(self, path):
        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(self.prefix_dict, indent=4))
