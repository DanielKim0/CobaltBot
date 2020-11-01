import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.eu4 import EU4Cog

class CobaltBot(commands.Bot):
    def __init__(self, prefix="!"):
        super().__init__(command_prefix=prefix)
        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')
        self.serv = os.getenv('DISCORD_SERVER')
        self.default_prefix = prefix
        # Prefixes should be different for different servers.
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

    # TODO below
    @commands.command(name="help")
    async def help(self, pass_context=True):
        # Help message sent as response to message in server in the person's DMs
        pass

    @commands.command(name="get_prefix", aliases=["prefix", "pre"])
    async def get_prefixes(self, ctx, name):
        pass

    @commands.command(name="set_prefix")
    async def set_prefixes(self, ctx, name):
        pass

    @commands.command(name="add", pass_context=True)
    async def add(self, ctx, name):
        self.add_cog(name)

    @commands.command(name="remove", pass_context=True)
    async def remove(self, ctx, name):
        self.remove_cog(name)

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
