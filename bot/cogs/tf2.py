import os
import discord
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import valve.source
import valve.source.a2s
import valve.source.master_server
from multiprocessing import Pool
import time

def lookup_address(address):
    """Function that looks up and fetches data from a particular address.
    
    Must be a module-level function, as class methods are not picklable and are therefore
    disallowed from being used in multiprocessing.
    
    Args:
        address (str): the address that is to be looked up.

    Returns:
        list: contains various pieces of data about the server corresponding to the address, else None.
    """

    try:
        with valve.source.a2s.ServerQuerier(address, timeout=.5) as server:
            info = server.info()
            return [info["player_count"], info["bot_count"], info["max_players"], info["server_name"], info["game"]]
    except (valve.source.messages.BrokenMessageError, valve.source.NoResponseError) as e:
        return None

class TF2Cog(CobaltCog):
    def __init__(self):
        super().__init__()

    def get_servers(self, region):
        """Method that fetches all of the server statistics for a given region."""

        with valve.source.master_server.MasterServerQuerier(timeout=1) as msq:
            servers = [x for x in msq.find(gamedir="tf", region=region, empty=False)]
            with Pool() as p:
                stats = p.map(lookup_address, servers)
                return stats

    @commands.command(name="tf2", description="", aliases=[], usage="")
    @check_valid_command
    async def tf2(self, ctx, players: int, region: str=""):
        """Wrapper that fetches tf2 server data and then displays it in discord.
        
        Also displays various error messages in certain cases.s"""

        if not region:
            region = "na"
        if region not in ["na-east", "na-west", "na", "sa", "eu", "as", "oc", "af", "rest", "all"]:
            await ctx.send("Invalid region!")
            return

        response = await ctx.send("Fetching server information...")
        
        servers = self.get_servers(region)
        valid = []
        for server in servers:
            if server is not None and server[0] - server[1] >= players:
                valid.append(server)
        valid = sorted(valid, reverse=True)
        
        messages = []
        if not valid:
            await ctx.send("No servers fit your criteria!")
        else:
            message = ""
            length = 0
            for server in valid:
                server[3] = server[3].replace("", "").replace("█", "")
                string = "{0}({1})/{2}\t{3}\n".format(*server)
                if length + len(string) >= 2000:
                    messages.append(message)
                    message = string
                    length = len(string)
                else:
                    message += string
                    length += len(string)
            messages.append(message)

            for message in messages:
                print(len(message))
                await ctx.send(message)
