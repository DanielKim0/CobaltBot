import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.eu4 import EU4Cog
from cogs.prefix import PrefixCog, fetch_prefix

class CobaltBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=fetch_prefix)
        p = PrefixCog("prefixes.json")
        self.add_cog(p)
        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')
        self.serv = os.getenv('DISCORD_SERVER')
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

    @commands.command(name="cog_add", pass_context=True)
    async def cog_add(self, ctx, cog: str):
        pass

    @commands.command(name="cog_remove", pass_context=True)
    async def cog_remove(self, ctx, cog: str):
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
