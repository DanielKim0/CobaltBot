import os
import discord
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


class PrefixCog(CobaltCog):
    def __init__(self):
        super().__init__()

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

    @commands.command(name="set_prefix")
    async def set_prefix(self, ctx, prefix: str):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            prefix_dict[guild] = [prefix]
            await ctx.send("This server's prefix has been set to this prefix: " + prefix)

    @commands.command(name="reset_prefix")
    async def reset_prefix(self, ctx):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in prefix_dict:
                prefix_dict.pop(guild)
                await ctx.send("This server's prefix has been set to the default prefix: !")
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
                else:
                    await ctx.send("The following prefix is not set for this server: " + prefix)
            else:
                await ctx.send("This server is currently set to the default prefix: !")
