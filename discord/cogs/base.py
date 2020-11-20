import os
import discord
from discord.ext import commands

def check_valid_command(func):
    print("checking")
    def wrapper(*args):
        obj = args[0]
        ctx = args[1]
        return ctx.guild.id in obj.added_servers
    return commands.check(wrapper)

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
