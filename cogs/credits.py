import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from colorama import Fore

class Credits(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Everyone that has worked on Melli
    @app_commands.command(name="credits", description="Meet the dev team.")
    async def creditscmd(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title="✨ Credits ✨",
                description="A heartfelt thank you to everyone who contributed to Melli!",
                color=0x5865F2  # A Discord blue shade
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1308048258337345609/1331874809352556597/f0a534c6da023d46a18674bcf5a6a147.png")
            embed.add_field(
                name="👨‍💻 Developers", 
                value="> `@_uncle_melo_`, `@pitr1010`, `@illtana`", 
                inline=False
            )
            embed.add_field(
                name="✍️ Editor", 
                value="> `@mizuki_mochizuki2090`", 
                inline=False
            )
            embed.add_field(
                name="🎨 Artists", 
                value="> `@soupinascoop`, `@bunnnl`", 
                inline=False
            )
            embed.set_footer(
                text="Thanks for supporting Melli!",
                icon_url="https://cdn.discordapp.com/emojis/1323527766011809873.webp"
            )

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred. Please contact an administrator.\n```{e}```", 
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Credits(bot))
