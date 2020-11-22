import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs.cobalt import CobaltCog, check_valid_command
import json
import difflib

class SMTCog(CobaltCog):
    def __init__(self):
        pass