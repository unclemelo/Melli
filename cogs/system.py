import discord
import json
import asyncio
import subprocess
import os
import sys
from datetime import datetime, timedelta
from discord import app_commands
from discord.ext import commands, tasks
from colorama import Fore


class System(commands.Cog):
    """
    A cog for managing system-level commands such as restarting, shutting down,
    and displaying bot uptime.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()  # Track when the bot started

    @staticmethod
    def restart_bot():
        """Restarts the bot using the current Python interpreter."""
        os.execv(sys.executable, ['python3'] + sys.argv)

    @staticmethod
    def update_code():
        """
        Pulls the latest code from the GitHub repository.
        
        Returns:
            str: The output of the Git pull operation.
        """
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
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Exception during Git pull: {e}")
            return str(e)

    def get_uptime(self):
        """Calculates and returns the bot's uptime."""
        now = datetime.utcnow()
        uptime = now - self.start_time
        return str(timedelta(seconds=uptime.total_seconds()))

    @commands.Cog.listener()
    async def on_ready(self):
        """Logs when the system cog is loaded."""
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} System cog loaded successfully.")

    @app_commands.command(name="reboot", description="Reboots the bot and updates its code.")
    @app_commands.checks.has_permissions(administrator=True)
    async def restart_cmd(self, interaction: discord.Interaction):
        """Reboots the bot after pulling the latest code from GitHub."""
        if interaction.user.id == 954135885392252940:
            embed = discord.Embed(
                title="Rebooting `MelonShield`...",
                description="Pulling updates from GitHub and restarting.",
                color=0x3df553
            )
            await interaction.response.send_message(embed=embed)

            # Pull latest code and check the result
            git_response = self.update_code()
            if "Already up to date" in git_response:
                embed.description += "\n\nNo updates found. Restarting with the current version."
            else:
                embed.description += "\n\nUpdates applied successfully."

            await interaction.followup.send(embed=embed)
            print("[ SYSTEM ] Rebooting bot...")
            self.restart_bot()
        else:
            await interaction.response.send_message("Sorry, only the developer can execute this command.")

    @app_commands.command(name="shutdown", description="Shuts down the bot.")
    @app_commands.checks.has_permissions(administrator=True)
    async def shutdown_cmd(self, interaction: discord.Interaction):
        """Shuts down the bot."""
        if interaction.user.id == 954135885392252940:
            embed = discord.Embed(
                title="Shutting Down `MelonShield`...",
                description="The bot is shutting down.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            print("[ SYSTEM ] Bot shutting down...")
            await self.bot.close()
        else:
            await interaction.response.send_message("Sorry, only the developer can execute this command.")

    @app_commands.command(name="uptime", description="Displays the bot's uptime.")
    async def uptime_cmd(self, interaction: discord.Interaction):
        """Sends the bot's uptime as a response."""
        uptime = self.get_uptime()
        embed = discord.Embed(
            title="Bot Uptime",
            description=f"`MelonShield` has been online for: **{uptime}**",
            color=0x3df553
        )
        await interaction.response.send_message(embed=embed)

    @tasks.loop(hours=12)
    async def reboot_loop(self):
        """
        Periodically pulls updates from GitHub and reboots the bot.
        Runs every 12 hours.
        """
        channel = self.bot.get_channel(1308048388637462558)
        embed = discord.Embed(
            title="Scheduled Reboot",
            description="Pulling updates from GitHub and restarting.",
            color=0x3df553
        )
        await channel.send(embed=embed)

        # Pull latest code and check the result
        git_response = self.update_code()
        if "Already up to date" in git_response:
            embed.description += "\n\nNo updates found. Restarting with the current version."
        else:
            embed.description += "\n\nUpdates applied successfully."

        await channel.send(embed=embed)
        print("[ SYSTEM ] Scheduled reboot initiated.")
        self.restart_bot()

    @reboot_loop.before_loop
    async def before_reboot_loop(self):
        """Waits until the bot is ready before starting the reboot loop."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    """Adds the System cog to the bot."""
    await bot.add_cog(System(bot))
