import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.eu4 import EU4Cog
from cogs.prefix import PrefixCog, fetch_prefix

class CobaltBot(commands.Bot):
    def __init__(self, cog_data, eu4_data):
        super().__init__(command_prefix=fetch_prefix)
        self.cog_data = cog_data
        self.add_cog(PrefixCog("prefixes.json")) # not included in cogs, valid for all servers
        self.cogs = {
            "eu4": EU4Cog(eu4_data[0], eu4_data[1], eu4_data[2], eu4_data[3])
        }
        for cog in self.cogs:
            self.add_cog(self.cogs[cog])
        self.load_cogs()
        
        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')

    async def on_ready(self):
        serv = os.getenv('DISCORD_SERVER')
        server = discord.utils.get(self.guilds, name=serv)

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

    async def save_cogs(self):
        cog_servers = dict()
        async with aiofiles.open(self.cog_data) as f:
            for cog in self.cogs:
                cog_servers[cog] = list(self.cogs[cog].servers)
            await f.write(json.dumps(data, indent=4))

    def load_cogs(self):
        with open(path, "r") as f:
            data = json.load(f)
        for cog in data:
            self.cogs[cog].servers = data[cog]

    def run(self):
        super().run(self.token)

if __name__ == "__main__":
    identifiers = "/home/daniel/Documents/discord/processing/eu4/results/names.json"
    full_data = "/home/daniel/Documents/discord/processing/eu4/results/full"
    impor_data = "/home/daniel/Documents/discord/processing/eu4/results/important"
    idea_data = "/home/daniel/Documents/discord/processing/eu4/results/ideas"
    cog_data = "/home/daniel/Documents/discord/bot_data/prefixes.json"
    bot = CobaltBot(cog_data, [identifiers, full_data, impor_data, idea_data])
    bot.run()
