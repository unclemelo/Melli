import discord
import json
import asyncio
import subprocess
import os
import sys
import re
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

    def get_update_channel(self) -> discord.TextChannel:
        """Fetches the update channel."""
        channel_id = 1310589613701857300  # Replace with your actual update channel ID
        return self.bot.get_channel(channel_id)

    @staticmethod
    def run_openai_migrate():
        """
        Executes the `openai migrate` command.
        """
        try:
            result = subprocess.run(
                ["openai", "migrate"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                print(f"{Fore.GREEN}[ OK ]{Fore.RESET} `openai migrate` successful:\n{result.stdout}")
            else:
                print(f"{Fore.RED}[ ERROR ]{Fore.RESET} `openai migrate` failed:\n{result.stderr}")
        except Exception as e:
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Exception during `openai migrate`: {e}")

    @staticmethod
    def restart_bot():
        """
        Runs `openai migrate` and restarts the bot using the current Python interpreter.
        """
        print("[ SYSTEM ] Running `openai migrate` before reboot...")
        System.run_openai_migrate()
        print("[ SYSTEM ] Restarting bot...")
        os.execv(sys.executable, ['python3'] + sys.argv)

    @staticmethod
    def update_code():
        """
        Pulls the latest code from the GitHub repository and updates Python dependencies.
        
        Returns:
            dict: A dictionary with the results of Git pull and pip install operations.
        """
        results = {"git_pull": None, "pip_install": None}

        # Step 1: Git Pull
        try:
            git_result = subprocess.run(
                ["git", "pull"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if git_result.returncode == 0:
                print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Git Pull Successful:\n{git_result.stdout}")
                results["git_pull"] = git_result.stdout
            else:
                print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Git Pull Failed:\n{git_result.stderr}")
                results["git_pull"] = git_result.stderr
        except Exception as e:
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Exception during Git pull: {e}")
            results["git_pull"] = str(e)
            return results  # Exit early if Git pull fails

        # Step 2: Update Python Dependencies
        try:
            pip_result = subprocess.run(
                ["python3", "-m", "pip", "install", "-r", "requirements.txt"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if pip_result.returncode == 0:
                print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Dependencies Updated Successfully:\n{pip_result.stdout}")
                results["pip_install"] = pip_result.stdout
            else:
                print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Failed to Update Dependencies:\n{pip_result.stderr}")
                results["pip_install"] = pip_result.stderr
        except Exception as e:
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Exception during pip install: {e}")
            results["pip_install"] = str(e)

        return results

    # The rest of the methods remain unchanged
    # ...

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

            # Pull latest code and notify update channel
            update_results = self.update_code()
            await self.notify_updates(update_results)  # Notify the update channel

            # Send feedback to the interaction user
            git_response = update_results.get("git_pull", "No Git response available.")
            if "Already up to date." in git_response:
                embed.description += "\n\n✨ No updates found. Restarting with the current version."
            else:
                embed.description += "\n\n🔧 Updates applied successfully."

            await interaction.followup.send(embed=embed)
            print("[ SYSTEM ] Rebooting bot...")
            self.restart_bot()
        else:
            await interaction.response.send_message("Sorry, only the developer can execute this command.")


async def setup(bot: commands.Bot):
    """Adds the System cog to the bot."""
    await bot.add_cog(System(bot))
