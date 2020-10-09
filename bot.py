# bot.py
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

    async def on_error(self, event, *args, **kwargs):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise

    @commands.command(name="add_cog", pass_context=True)
    async def add_cog(self, ctx, name):
        super().add_cog(name)

    @commands.command(name="remove_cog", pass_context=True)
    async def remove_cog(self, ctx, name):
        super().remove_cog(name)

    def run(self):
        super().run(self.token)

bot = CobaltBot()
bot.run()