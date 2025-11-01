import discord
import subprocess
import os
import sys
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from functools import wraps

## Developer IDs ##
devs = {954135885392252940, 667032667732312115}      
###################

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
    ## Replace with your update channel ID ##
    UPDATE_CHANNEL_ID = 1434070857696804965
    #########################################

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.devs = devs

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
                   "Updates applied. Check the [GitHub Page](<https://github.com/unclemelo/Melli>)"), # Replace username & repo_name
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
            "git_pull": self.run_command(["git", "pull"]),
            "pip_install": self.run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt"])
        }

    @app_commands.command(name="update", description="Reboots the bot and updates its code.")
    @is_dev()
    async def restart_cmd(self, interaction: discord.Interaction):
        """Command to update the bot and pull updates from GitHub."""
        embed = discord.Embed(
            title="Updating...",
            description="Pulling updates from GitHub and restarting.",
            color=0x3474eb
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        update_results = self.update_code()
        await self.notify_updates(update_results)

        git_response = update_results.get("git_pull", "No Git response available.")

        if "already up to date." in git_response.lower():
            embed.description += "\n\nNo updates found. Cancelling the reboot..."
        elif "error" in git_response.lower() or "conflict" in git_response.lower():
            embed.description += "\n\n🚨 Error: Merge conflict or issue detected. Update failed!"
        else:
            embed.description += "\n\n🔧 Updates applied successfully."
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        if "already up to date." in git_response.lower():
            pass
        elif "error" in git_response.lower() or "conflict" in git_response.lower():
            pass
        else:
            print("[ SYSTEM ] Rebooting bot...")
            self.restart_bot()

async def setup(bot: commands.Bot):
    """Adds the Updater cog to the bot."""
    await bot.add_cog(Updater(bot))
