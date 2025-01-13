import discord, json, random
import asyncio
from discord.ext.commands import cooldown, BucketType
from datetime import timedelta
from colorama import Fore
from discord import app_commands
from discord.ext import commands

class VoteToKick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

async def setup(bot: commands.Bot):
    await bot.add_cog(VoteToKick(bot))