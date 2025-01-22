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
            embed = discord.Embed(title="Cheese", description="Do you like cheese?")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1330523346890395764/1331709220785229994/cheese.gif?ex=67929a5c&is=679148dc&hm=3362790ed38cab48622004e784c336fafea720fe0dd2672795ce29a2dbce47f9&")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred. Please contact an administrator.\n```{e}```", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Cheese(bot))