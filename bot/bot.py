import os
import random
import discord
import json
from dotenv import load_dotenv
from discord.ext import commands
from cogs.prefix import PrefixCog, fetch_prefix
from cogs.basic import BasicCog
from cogs.eu4 import EU4Cog
from cogs.smt import SMTCog

class CobaltBot(commands.Bot):
    def __init__(self, cog_data, prefix_data, eu4_data, smt_data):
        super().__init__(command_prefix=fetch_prefix)
        self.prefix = PrefixCog(prefix_data)
        self.basic = BasicCog(cog_data)
        self.add_cog(self.prefix) # not included in cogs, valid for all servers
        self.basic.cog_dict = {
            "eu4": EU4Cog(eu4_data[0], eu4_data[1], eu4_data[2], eu4_data[3]),
            "smt": SMTCog(smt_data[0], smt_data[1], smt_data[2], smt_data[3]),
        }

        self.add_cog(self.basic)
        self.basic.load_cogs()
        for cog in self.basic.cog_dict:
            self.add_cog(self.basic.cog_dict[cog])
        
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

    def run(self):
        super().run(self.token)

if __name__ == "__main__":
    identifiers = "/home/daniel/Documents/discord/processing/eu4/results/names.json"
    full_data = "/home/daniel/Documents/discord/processing/eu4/results/full"
    impor_data = "/home/daniel/Documents/discord/processing/eu4/results/important"
    idea_data = "/home/daniel/Documents/discord/processing/eu4/results/ideas"
    eu4_data = [identifiers, full_data, impor_data, idea_data]

    stats = "/home/daniel/Documents/discord/processing/smt/results/demons"
    fusions = "/home/daniel/Documents/discord/processing/smt/results/fusions"
    fissions = "/home/daniel/Documents/discord/processing/smt/results/fissions"
    names = "/home/daniel/Documents/discord/processing/smt/results/demon_names.json"
    smt_data = [stats, fusions, fissions, names]

    cog_data = "/home/daniel/Documents/discord/bot_data/cogs.json"
    prefix_data = "/home/daniel/Documents/discord/bot_data/prefixes.json"

    bot = CobaltBot(cog_data, prefix_data, eu4_data, smt_data)
    bot.run()