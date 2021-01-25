import os
import discord
from discord.ext import commands
import functools
import json
import difflib

def check_valid_command(func):
    """Decorator that checks if a particular discord function call is allowed for a server.

    Needs to be a module-level function because decorators don't recognize self at class definition 
    time, so I have to pass the self object indirectly through the inputted function instead.

    Args:
        func (function): the function inputted through the decorator.

    Returns:
        function: the inputted function wrapped by functools if command is valid, else None."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        obj = args[0]
        ctx = args[1]
        if ctx.guild and ctx.guild.id in obj.added_servers:
            return await func(*args)
        else:
            return None
    return wrapper
 
class CobaltCog(commands.Cog):
    """Parent class for this project's cogs, handling permissions and containing utility functions.

    Attributes:
        added_servers (set): a set containing server IDs that are valid for this cog."""

    def __init__(self):
        super().__init__()
        self.added_servers = set()
    
    async def make_embed(self, data, inline=True):
        """Function that generates a discord embed from the data that it is given.
        
        Args:
            data (dict): dict that contains data on what to put in the embed. 
            inline (bool): whether to make the embed inline or not.

        Returns:
            discord.File: image file if the embed contains an image, else None.
            discord.Embed: the actual discord embed object."""
        
        image = None
        embed = discord.Embed(title = data["title"])
        for i in range(len(data["fields"])):
            embed.add_field(name=data["fields"][i], value=data["messages"][i], inline=inline)
            
        if "image_path" in data and data["image_path"]:
            img_name = os.path.basename(data["image_path"])
            image = discord.File(data["image_path"], filename = img_name)
            embed.set_thumbnail(url="attachment://" + img_name)
        return image, embed

    async def add_server(self, ctx):
        """Method that adds a server to a cog's permissions list."""

        server_id = ctx.guild.id
        if server_id in self.added_servers:
            await ctx.send("Cog already added!")
        else:
            self.added_servers.add(server_id)
            await ctx.send("Cog added!")

    async def remove_server(self, ctx):
        """Method that removes a server from a cog's permissions list."""

        server_id = ctx.guild.id
        if server_id not in self.added_servers:
            await ctx.send("Cog already not enabled!")
        else:
            self.added_servers.remove(server_id)
            await ctx.send("Cog removed!")

    async def nearest_spelling(self, ctx, string, names):
        """Method that responds to an input by saying the nearest spellings of a string from a list.

        If the string is in the list, the function just returns the string instead.
        Else, the method responds to the ctx by saying an error message listing the nearest spellings.
        Used with functions that input one out of many possible string arguments.

        Args:
            strint (str): the string to compare.
            names (list-like): the collection of strings that are compared to.

        Returns:
            str: the inputted string if it's in names, else None."""

        string = string.lower()
        if string in names:
            return string
        else:
            matches = difflib.get_close_matches(string, names)
            if matches:
                message = "Sorry, I couldn't find any matches for " + string + ".\nDid you mean "
                for item in matches[:-1]:
                    message += item + " or "
                message += matches[-1] + "?"
            else:
                message = "Sorry, I couldn't find any matches for " + string + "."
            await ctx.send(message)
            return None

    async def fetch_embed(self, string, path, inline=True):
        """Wrapper function for self.make_embed that fetches data from a file and makes an embed from it."""

        filename = os.path.join(path, string + ".json")
        with open(filename, "r") as f:
            data = json.load(f)
        image, embed = await self.make_embed(data, inline)
        return image, embed
