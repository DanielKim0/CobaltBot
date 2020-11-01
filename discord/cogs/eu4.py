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
        super().__init__(bot, identifiers, full_data, impor_data, idea_data)
        self.name_map = json.load(identifiers)
        self.identifiers = set(self.name_map.keys)
        self.full_data = full_data
        self.impor_data = impor_data
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

    async def fetch_embed(self, string, path):
        filename = os.path.join(path, string + ".json")
        data = json.load(filename)
        embed = await self.make_embed(data)
        return embed

    @valid_cog_check
    @commands.command(name=data, description="", aliases=[], usage="")
    async def fetch_idea(self, ctx, string: str, full_data: str):
        string = await self.nearest_spelling(ctx, string)
        if string is not None:
            if full_data in ["all", "full", "complete"]:
                embed = await self.fetch_embed(ctx, string, self.full_data)
            elif full_data in ["imp", "impor", "important"]
                embed = await self.fetch_embed(ctx, string, self.impor_data)
            else:
                embed = await self.fetch_embed(ctx, string, self.idea_data)
            await ctx.send(embed)
