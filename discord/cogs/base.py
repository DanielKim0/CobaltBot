import os
import discord
from discord.ext import commands

async def valid_cog_check(ctx, msg="Error: This server is not configured to use this command."):
    # Function that checks if the cog is usable in this server
    valid = args[0].name in args[0].bot.cog_dict[ctx.message.guild.id]
    if not valid:
        await ctx.send(msg)
    return valid

class CobaltCog(commands.Cog):
    def __init__(self):
        pass
    
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
