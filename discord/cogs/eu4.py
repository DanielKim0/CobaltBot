import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from ../bot import CobaltCog
import json
import difflib

class EU4Cog(CobaltCog):
    def __init__(self, bot):
        super().__init__(bot, cog_name, identifiers, tag_data, idea_data)
        self.name_map = json.load(identifiers)
        self.identifiers = set(self.name_map.keys)
        self.tag_data = tag_data
        self.idea_data = idea_data

    async def nearest_spelling(self, ctx, string):
        if string in self.identifiers:
            return string
        else:
            matches = difflib.get_close_matches(string)
            message = "Sorry, I couldn't find any matches for this country/tag.\nDid you mean "
            for item in matches[:-1]:
                message += item + " or "
            message += matches[-1] + "?"
            await ctx.send(message)
            return None

    async def parse_idea(self, ctx, data):

    async def parse_data(self, ctx, data):

    @valid_cog_check
    @commands.command(name=idea, description="", aliases=[], usage="")
    async def fetch_idea(self, ctx, string, full_data=""):
        string = await self.nearest_spelling(ctx, string)
        if string is not None:
            data = json.load()
            if full_data in ["data", "full"]:
                await self.parse_data(ctx, data)
            else:
                await self.parse_idea(ctx, data)
