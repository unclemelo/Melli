import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from colorama import Fore

class Cheese(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="cheese", description="cheese")
    async def cheesecmd(self, interaction: discord.Interaction):
        try:            
            embed = discord.Embed(title="Cheese", description="https://tenor.com/view/cheese-gif-25732604", color=0x3474eb)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred. Please contact an administrator.\n```{e}```", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Cheese(bot))