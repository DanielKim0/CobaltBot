import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.eu4 import EU4Cog

prefix_dict = dict()
def get_prefix(bot, message):
    prefixes = ["!"]

    if not message.guild:
        return "!"
    if message.guild.id in prefix_dict:
        prefixes = prefix_dict[message.guild.id]

    return commands.when_mentioned_or(*prefixes)(bot, message)

class CobaltBot(commands.Bot):
    def __init__(self, prefix="!"):
        super().__init__(command_prefix=get_prefix)
        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')
        self.serv = os.getenv('DISCORD_SERVER')
        # Prefixes should be different for different servers.
        self.prefixes = dict()
        # Certain cogs should be admitted for different servers.
        self.cog_dict = dict()

    async def on_ready(self):
        server = discord.utils.get(self.guilds, name=self.serv)

        print(
            f'{self.user} is connected to the following server:\n'
            f'{server.name}(id: {server.id})'
        )

    async def on_error(self, event, *args, **kwargs):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise

    # TODO below
    @commands.command(name="help")
    async def help(self, pass_context=True):
        # Help message sent as response to message in server in the person's DMs
        pass

    async def guild_check(self, ctx):
        if not ctx.guild:
            await ctx.send("Error: Prefixes cannot be changed in DMs, only servers.")
        return ctx.guild

    @commands.command(name="get_prefix", aliases=["prefix", "pre"])
    async def get_prefix(self, ctx, name):
        if await self.guild_check(ctx):
            guild = ctx.guild.id
            if guild in prefix_dict:
                prefixes = prefix_dict[guild]
                await ctx.send("This server has the following custom prefixes: " + " ".join(prefixes))
            else:
                await ctx.send("This server is using the default prefix: !")

    @commands.command(name="add_prefix")
    async def add_prefix(self, ctx, name, prefix: str):
        if await self.guild_check:
            guild = ctx.guild.id
            prefix_dict[guild] = prefix
            await ctx.send("This server's prefix has been set to this prefix: " + prefix)

    @commands.command(name="set_prefix")
    async def set_prefix(self, ctx, name, prefix: str):
        if await self.guild_check:
            guild = ctx.guild.id
            prefix_dict[guild] = prefix
            await ctx.send("This server's prefix has been set to this prefix: " + prefix)

    @commands.command(name="reset_prefix")
    async def reset_prefix(self, ctx, name):
        if await self.guild_check:
            guild = ctx.guild.id
            if guild in prefix_dict:
                prefix_dict.pop(guild)
                await ctx.send("This server's prefix has been set to the default prefix: !")
            else:
                await ctx.send("This server is already set to the default prefix: !")
        
    @commands.command(name="remove_prefix")
    async def remove_prefix(self, ctx, name, prefix: str):
        if await self.guild_check:
            guild = ctx.guild.id
            if guild in prefix_dict:
                if prefix in prefix_dict[guild]:
                    prefix_dict[guild].remove(prefix)
                    await ctx.send("This following prefix has been removed from this server: " + prefix)
                else:
                    await ctx.send("The following prefix is not set for this server: " + prefix)
            else:
                await ctx.send("This server is currently set to the default prefix: !")

    @commands.command(name="cog_add", pass_context=True)
    async def cog_add(self, ctx, name):
        pass

    @commands.command(name="cog_remove", pass_context=True)
    async def cog_remove(self, ctx, name):
        pass

    def run(self):
        super().run(self.token)

if __name__ == "__main__":
    bot = CobaltBot()
    identifiers = "/home/daniel/Documents/discord/processing/eu4/results/names.json"
    full_data = "/home/daniel/Documents/discord/processing/eu4/results/full"
    impor_data = "/home/daniel/Documents/discord/processing/eu4/results/important"
    idea_data = "/home/daniel/Documents/discord/processing/eu4/results/ideas"
    eu4 = EU4Cog(identifiers, full_data, impor_data, idea_data)
    bot.add_cog(eu4)
    bot.run()
