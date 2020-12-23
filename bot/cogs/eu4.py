import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import json

class EU4Cog(CobaltCog):
    """Cog that handles eu4 functionality.

    Attributes:
        identifiers (dict): maps various tag names to tags.
        full_data (str): path to a folder containing full tag data.
        impor_data (str): path to a folder containing important tag data.
        idea_data (str): path to a folder containing idea-only tag data."""

    def __init__(self, identifiers, full_data, impor_data, idea_data):
        super().__init__()
        with open(identifiers, "r") as f:
            self.name_map = json.load(f)
        self.identifiers = set(self.name_map.keys())
        self.full_data = full_data
        self.impor_data = impor_data
        self.idea_data = idea_data

    @commands.command(name="eu4", help="Fetches data about an eu4 tag.")
    @check_valid_command
    async def fetch_data(self, ctx, string: str, full_data: str=""):
        """Method that fetches tag data from the requisite file and displays it as an embed."""
        
        string = await self.nearest_spelling(ctx, string, self.identifiers)
        if string is not None:
            string = self.name_map[string]
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
