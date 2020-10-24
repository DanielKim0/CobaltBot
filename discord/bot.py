import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands


class CobaltBot(commands.Bot):
    def __init__(self, prefix="!"):
        super().__init__(command_prefix=prefix)
        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')
        self.serv = os.getenv('DISCORD_SERVER')
        self.default_prefix = prefix
        self.prefixes = dict()
        # Certain cogs should be admitted for different servers.
        self.cog_dict = dict()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        server = discord.utils.get(self.guilds, name=self.serv)

        print(
            f'{self.user} is connected to the following server:\n'
            f'{server.name}(id: {server.id})'
        )

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, welcome to my Discord server!'
        )

    async def determine_prefix(self, message):
        guild = message.guild
        if guild:
            return self.prefixes[guild]
        else:
            return self.default_prefix

    async def on_error(self, event, *args, **kwargs):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise

    @commands.command(name="help")
    async def help(self, pass_context=True):
        # TODO
        pass

    @commands.command(name="get_prefix", aliases=["prefix", "pre"])
    async def get_prefixes(self, ctx, name):
        pass

    @commands.command(name="set_prefix")
    async def set_prefixes(self, ctx, name):
        pass

    @commands.command(name="add_cog", pass_context=True)
    async def add_cog(self, ctx, name):
        self.add_cog(name)

    @commands.command(name="remove_cog", pass_context=True)
    async def remove_cog(self, ctx, name):
        self.remove_cog(name)

    def run(self):
        self.run(self.token)

bot = CobaltBot()
bot.run()