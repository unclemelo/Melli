import discord, json, asyncio, subprocess, os, sys

from datetime import timedelta
from colorama import Fore
from discord import app_commands
from discord.ext import commands, tasks

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
    
    @app_commands.command(name="reboot", description="reboots the bot.")
    @app_commands.checks.has_permissions(administrator=True)
    async def restart_cmd(self, interaction: discord.Interaction):
        await interaction.response.send_message("Rebooting `MeloGames`...")
        restart_bot()

    @tasks.loop(hours=24)
    async def reboot_loop(self):
        channel = self.bot.get_channel(1308048388637462558)
        embed = discord.Embed(title="Rebooting `MelonShield`...", description="`MelonShield` is now updating all its code...", color=0x3df553)
        await channel.send(embed=embed)
        restart_bot()

    @reboot_loop.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready


	

async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
