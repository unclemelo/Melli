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
from functools import wraps

# Developer IDs
devs = [667032667732312115, 954135885392252940, 1186435491252404384, 641822140362129408]

def is_dev():
    """A decorator to restrict commands to developers."""
    def predicate(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if interaction.user.id in self.devs:
                return await func(self, interaction, *args, **kwargs)
            else:
                await interaction.response.send_message(
                    "Sorry, this command is restricted to developers.", ephemeral=True
                )
        return wrapper
    return predicate

class System(commands.Cog):
    """
    A cog for managing system-level commands such as restarting, shutting down,
    and displaying bot uptime.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()  # Track when the bot started
        self.bot.tree.on_error = self.on_tree_error
        self.devs = devs

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Take a chill pill! Command is cooling off. Try again in **{error.retry_after:.2f}** seconds.", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("LOL, you thought? Not enough perms, buddy.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{error}")
            print(f"An error occurred: {error}")
            raise error

    def get_update_channel(self) -> discord.TextChannel:
        """Fetches the update channel."""
        channel_id = 1308048388637462558
        return self.bot.get_channel(channel_id)

    def summarize_pip_output(self, pip_output: str) -> str:
        """
        Summarizes pip install output for better readability, removing version constraints.
        Args:
            pip_output (str): The raw pip install output.
        Returns:
            str: A condensed summary of the pip output.
        """
        lines = pip_output.splitlines()
        summary = []

        for line in lines:
            if "Requirement already satisfied" in line:
                parts = line.split()
                package = parts[3]  # Package name
                version = parts[-1].strip("()")  # Version inside parentheses
                package = re.sub(r'[<>=!~]+[0-9.]+', '', package).strip()
                summary.append(f"- {package}: ({version})")
            elif "Successfully installed" in line:
                installed = line.replace("Successfully installed", "").strip()
                summary.append(f"Installed: {installed}")

        return "\n".join(summary) if summary else "No changes."

    async def notify_updates(self, update_results: dict):
        """
        Sends update notifications to the designated update channel.
        Args:
            update_results (dict): Results of the update process.
        """
        channel = self.get_update_channel()
        if channel is None:
            print("[ ERROR ] Update channel not found.")
            return

        embed = discord.Embed(
            title="🔄 Bot Updated",
            description="The bot has successfully pulled updates from GitHub and restarted.",
            color=0x3474eb,
            timestamp=datetime.utcnow()
        )

        git_response = update_results.get("git_pull", "No Git response available.")
        updated_files = update_results.get("updated_files", [])

        if "Already up to date." in git_response:
            embed.add_field(
                name="GitHub Status",
                value="✨ No updates found. The bot is running the latest version.",
                inline=False
            )
        else:
            updates = "\n".join(f"- `{file}`" for file in updated_files) if updated_files else "No specific files listed."
            if len(updates) > 1024:  # Truncate if necessary
                updates = updates[:1021] + "..."
            embed.add_field(
                name="🔧 Applied Updates",
                value=f"**Updated Files/Commits:**\n{updates}",
                inline=False
            )

        pip_response = update_results.get("pip_install", "No dependency update response.")
        pip_summary = self.summarize_pip_output(pip_response)
        embed.add_field(
            name="📦 Dependencies",
            value=f"```{pip_summary}```" if pip_summary else "No changes.",
            inline=False
        )

        await channel.send(embed=embed)

    @staticmethod
    def restart_bot():
        """Restarts the bot using the current Python interpreter."""
        os.execv(sys.executable, ['python3'] + sys.argv)

    @staticmethod
    def update_code():
        """
        Pulls the latest code from the GitHub repository and updates Python dependencies.
        
        Returns:
            dict: A dictionary with the results of Git pull and pip install operations.
        """
        results = {"git_pull": None, "pip_install": None}

        try:
            git_result = subprocess.run(
                ["git", "pull"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            results["git_pull"] = git_result.stdout if git_result.returncode == 0 else git_result.stderr
        except Exception as e:
            results["git_pull"] = str(e)
            return results

        try:
            pip_result = subprocess.run(
                ["python3", "-m", "pip", "install", "-r", "requirements.txt"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            results["pip_install"] = pip_result.stdout if pip_result.returncode == 0 else pip_result.stderr
        except Exception as e:
            results["pip_install"] = str(e)

        return results

    def get_uptime(self):
        """Calculates and returns the bot's uptime."""
        now = datetime.utcnow()
        uptime = now - self.start_time
        return str(timedelta(seconds=uptime.total_seconds()))

    @app_commands.command(name="reboot", description="Reboots the bot and updates its code.")
    @is_dev()
    async def restart_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Rebooting `Melli`...",
            description="Pulling updates from GitHub and restarting.",
            color=0x3474eb
        )
        await interaction.response.send_message(embed=embed, delete_after=5)

        update_results = self.update_code()
        await self.notify_updates(update_results)

        git_response = update_results.get("git_pull", "No Git response available.")
        if "Already up to date." in git_response:
            embed.description += "\n\n✨ No updates found. Restarting with the current version."
        else:
            embed.description += "\n\n🔧 Updates applied successfully."

        await interaction.followup.send(embed=embed)
        print("[ SYSTEM ] Rebooting bot...")
        self.restart_bot()

    @app_commands.command(name="shutdown", description="Shuts down the bot.")
    @is_dev()
    async def shutdown_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Shutting Down `Melli`...",
            description="The bot is shutting down.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, delete_after=5)
        print("[ SYSTEM ] Bot shutting down...")
        await self.bot.close()

    @app_commands.command(name="uptime", description="Displays the bot's uptime.")
    async def uptime_cmd(self, interaction: discord.Interaction):
        uptime = self.get_uptime()
        embed = discord.Embed(
            title="Bot Uptime",
            description=f"`Melli` has been online for: **{uptime}**",
            color=0x3474eb
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    """Adds the System cog to the bot."""
    await bot.add_cog(System(bot))
