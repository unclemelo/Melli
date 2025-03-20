import discord
import subprocess
import os
import sys
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from functools import wraps

# Developer IDs
devs = {667032667732312115, 954135885392252940, 1186435491252404384, 641822140362129408}

def is_dev():
    """Decorator to restrict commands to developers."""
    def predicate(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if interaction.user.id in self.devs:
                return await func(self, interaction, *args, **kwargs)
            await interaction.response.send_message(
                "This command is restricted to developers.", ephemeral=True
            )
        return wrapper
    return predicate

class Updater(commands.Cog):
    """Cog for managing system-level commands like restarting and updating the bot."""
    UPDATE_CHANNEL_ID = 1308048388637462558

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.bot.tree.on_error = self.on_tree_error
        self.devs = devs

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handles errors occurring in app commands."""
        error_messages = {
            app_commands.CommandOnCooldown: f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            app_commands.MissingPermissions: "You lack the necessary permissions for this command."
        }
        
        message = error_messages.get(type(error), str(error))
        await interaction.response.send_message(message, ephemeral=True)
        if not isinstance(error, (app_commands.CommandOnCooldown, app_commands.MissingPermissions)):
            print(f"[ ERROR ] {error}")
            raise error

    def get_update_channel(self) -> discord.TextChannel:
        """Fetches the update channel."""
        return self.bot.get_channel(self.UPDATE_CHANNEL_ID)

    async def notify_updates(self, update_results: dict):
        """Sends update notifications to the designated update channel."""
        channel = self.get_update_channel()
        if not channel:
            print("[ ERROR ] Update channel not found.")
            return

        embed = discord.Embed(
            title="Bot Updated",
            description="Successfully pulled updates from GitHub and restarted.",
            color=0x3474eb,
            timestamp=datetime.utcnow()
        )
        
        git_response = update_results.get("git_pull", "No Git response available.")
        embed.add_field(
            name="GitHub Status",
            value=("No updates found. The bot is running the latest version."
                   if "Already up to date." in git_response else
                   "Updates applied. Check the [GitHub Page](<https://github.com/unclemelo/Melli>)"),
            inline=False
        )
        await channel.send(embed=embed)

    @staticmethod
    def restart_bot():
        """Restarts the bot using the current Python interpreter."""
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @staticmethod
    def run_command(command: list) -> str:
        """Runs a shell command and returns the output."""
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return str(e)
    
    def update_code(self) -> dict:
        """Pulls the latest code from GitHub and updates dependencies."""
        return {
            "update_server": self.run_command(["sudo", "apt", "update", "&&", "sudo", "apt", "upgrade"]),
            "git_pull": self.run_command(["git", "pull"]),
            "pip_install": self.run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt"])
        }

    @app_commands.command(name="update", description="Reboots the bot and updates its code.")
    @is_dev()
    async def restart_cmd(self, interaction: discord.Interaction):
        """Command to update the bot and pull updates from GitHub."""
        embed = discord.Embed(
            title="Updating...",
            description="Pulling updates from GitHub & Ubuntu and restarting.",
            color=0x3474eb
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        update_results = self.update_code()
        await self.notify_updates(update_results)

        git_response = update_results.get("git_pull", "No Git response available.")
        embed.description += "\n\nNo updates found. Cancelling the reboot..." if "Already up to date." in git_response else "\n\n🔧 Updates applied successfully."
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        if "Already up to date." in git_response:
            pass
        else:
            print("[ SYSTEM ] Rebooting bot...")
            self.restart_bot()

async def setup(bot: commands.Bot):
    """Adds the Updater cog to the bot."""
    await bot.add_cog(Updater(bot))
