import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from ../bot import CobaltCog
import json

class EU4Cog(CobaltCog):
    def __init__(self, bot):
        super().__init__(bot, name)
        self.names = self.load_names("")

    def load_names(self, path):
        pass
    
    async def nearest_spelling(self, string):
        pass

    async def load_file(self, tag):
        pass

    async def parse_idea(self, data):
        pass

    async def parse_data(self, data):
        pass

    @valid_cog_check
    @commands.command(name=idea, description="", aliases=[], usage="")
    async def fetch_idea(self, ctx):
        pass