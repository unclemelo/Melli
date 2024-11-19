import discord
from discord.ext import commands
from datetime import timedelta
from discord import app_commands
from colorama import Fore

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded misc.py")

    @app_commands.command(name="allowed_links", description="Shows all the allowed links")
    async def allowedlinks(self, interaction: discord.Interaction):
        allowed_links = "https://c.tenor.com/, https://cdn.discordapp.com/, https://imgflip.com/, https://media.discordapp.net/, https://on.soundcloud.com/, https://open.spotify.com/, https://tenor.com/, https://www.bilibili.com/, https://www.youtube.com/, https://youtu.be/, https://youtube.com/"
        embed = discord.Embed(title="Allowed Links Below ⬇️", description=f"🔗 - {allowed_links} - 🔗")
        await interaction.response.send_message(embed=embed)



async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
