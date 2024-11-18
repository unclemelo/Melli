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

    def update_code(self):
        """Pull the latest code from the GitHub repository."""
        try:
            result = subprocess.run(
                ["git", "pull"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if result.returncode == 0:
                print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Git Pull Successful:\n{result.stdout}")
                return result.stdout
            else:
                print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Git Pull Failed:\n{result.stderr}")
                return result.stderr
        except Exception as e:
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Exception during git pull: {e}")
            return str(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded system.py")
    
    @app_commands.command(name="reboot", description="Reboots the bot and updates its code.")
    @app_commands.checks.has_permissions(administrator=True)
    async def restart_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Rebooting `MelonShield`...",
            description="`MelonShield` is now pulling updates from GitHub and rebooting.",
            color=0x3df553
        )
        await interaction.response.send_message(embed=embed)

        # Pull latest code
        git_response = self.update_code()
        if "Already up to date" in git_response:
            embed.description += "\n\nNo updates found, restarting with the current version."
        else:
            embed.description += "\n\nUpdates applied successfully."

        await interaction.followup.send(embed=embed)
        print("Rebooting...")
        restart_bot()

    @tasks.loop(hours=24)
    async def reboot_loop(self):
        channel = self.bot.get_channel(1308048388637462558)
        embed = discord.Embed(
            title="Rebooting `MelonShield`...",
            description="`MelonShield` is now pulling updates from GitHub and rebooting.",
            color=0x3df553
        )
        await channel.send(embed=embed)

        # Pull latest code
        git_response = self.update_code()
        if "Already up to date" in git_response:
            embed.description += "\n\nNo updates found, restarting with the current version."
        else:
            embed.description += "\n\nUpdates applied successfully."

        await channel.send(embed=embed)
        print("Rebooting...")
        restart_bot()

    @reboot_loop.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready


async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
