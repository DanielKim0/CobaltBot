import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.base import CobaltCog
import json
import difflib

class EU4Cog(CobaltCog):
    def __init__(self, identifiers, full_data, impor_data, idea_data):
        super().__init__()
        with open(identifiers, "r") as f:
            self.name_map = json.load(f)
        self.identifiers = set(self.name_map.keys())
        self.full_data = full_data
        self.impor_data = impor_data
        self.idea_data = idea_data

    async def nearest_spelling(self, ctx, string):
        string = string.lower()
        if string in self.identifiers:
            return self.name_map[string]
        else:
            matches = difflib.get_close_matches(string, self.identifiers)
            message = "Sorry, I couldn't find any matches for this country/tag.\nDid you mean "
            for item in matches[:-1]:
                message += item + " or "
            message += matches[-1] + "?"
            await ctx.send(message)
            return None

    async def fetch_embed(self, string, path, inline=True):
        filename = os.path.join(path, string + ".json")
        with open(filename, "r") as f:
            data = json.load(f)
        image, embed = await self.make_embed(data, inline)
        return image, embed

    # @valid_cog_check
    @commands.command(name="eu4", description="", aliases=[], usage="")
    async def fetch_idea(self, ctx, string: str, full_data: str=""):
        string = await self.nearest_spelling(ctx, string)
        if string is not None:
            if full_data in ["all", "full", "complete"]:
                image, embed = await self.fetch_embed(string, self.full_data, False)
            elif full_data in ["imp", "impor", "important"]:
                image, embed = await self.fetch_embed(string, self.impor_data, False)
            else:
                image, embed = await self.fetch_embed(string, self.idea_data, False)
            
            if image:
                await ctx.send(file=image, embed=embed)
            else:
                await ctx.send(embed=embed)
