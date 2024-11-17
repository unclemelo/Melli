import discord, json, asyncio, subprocess, os, sys

from datetime import timedelta
from colorama import Fore
from discord import app_commands
from discord.ext import commands

def restart_bot(): 
    os.execv(sys.executable, ['python3'] + sys.argv)

class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    
    def restart_bot(self): 
        os.execv(sys.executable, ['python3'] + sys.argv)
    

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded system.py")
    
    @app_commands.command(name="test", description="Testing command")
    @app_commands.checks.has_permissions(administrator=True)
    async def test_cmd(self, interaction: discord.Interaction):
        await interaction.response.send_message("**\"Shut up Melo, I'm trying to sleep unlike you. <:9437animeshutup:1293927061530083409>\"**")
    
    @app_commands.command(name="reboot", description="reboots the bot.")
    @app_commands.checks.has_permissions(administrator=True)
    async def restart_cmd(self, interaction: discord.Interaction):
        await interaction.response.send_message("Rebooting `MeloGames`...")
        restart_bot()


	

async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
