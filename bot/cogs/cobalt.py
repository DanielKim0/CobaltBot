import os
import discord
from discord.ext import commands
import functools
import json
import difflib

def check_valid_command(func):
    @functools.wraps(func)
    async def wrapper(*args):
        obj = args[0]
        ctx = args[1]
        if ctx.guild.id in obj.added_servers:
            return await func(*args)
        else:
            return None
    return wrapper
 
class CobaltCog(commands.Cog):
    def __init__(self):
        super().__init__()
        self.added_servers = set()
    
    async def make_embed(self, data, inline=True):
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
        server_id = ctx.guild.id
        if server_id in self.added_servers:
            await ctx.send("Cog already added!")
        else:
            self.added_servers.add(server_id)
            await ctx.send("Cog added!")

    async def remove_server(self, ctx):
        server_id = ctx.guild.id
        if server_id not in self.added_servers:
            await ctx.send("Cog already not enabled!")
        else:
            self.added_servers.remove(server_id)
            await ctx.send("Cog removed!")

    async def nearest_spelling(self, ctx, string, names):
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
        filename = os.path.join(path, string + ".json")
        with open(filename, "r") as f:
            data = json.load(f)
        image, embed = await self.make_embed(data, inline)
        return image, embed
