import discord
import subprocess
import os
import sys
from datetime import datetime, timezone
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
        git_pull_output = self.run_command(["git", "pull"])
        pip_output = self.run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt"])

        # Fetch the last few commit messages for display
        if "Already up to date." in git_pull_output:
            commit_logs = None
        else:
            commit_logs = self.run_command(["git", "log", "-n", "3", "--pretty=format:• %s (%an)"])

        return {
            "git_pull": git_pull_output,
            "pip_install": pip_output,
            "commit_logs": commit_logs
        }

    async def notify_updates(self, update_results: dict):
        """Sends update notifications to the designated update channel."""
        channel = self.get_update_channel()
        if not channel:
            print("[ ERROR ] Update channel not found.")
            return

        embed = discord.Embed(
            title="Bot Updated",
            description="Successfully pulled updates from GitHub and restarted.",
            color=0x3474eb
        )

        git_response = update_results.get("git_pull", "No Git response available.")
        commit_logs = update_results.get("commit_logs")

        # --- Add GitHub status ---
        embed.add_field(
            name="GitHub Status",
            value=("No updates found. The bot is running the latest version."
                   if "Already up to date." in git_response
                   else "Updates applied successfully. Check the [GitHub Page](<https://github.com/unclemelo/Melli>)"),
            inline=False
        )

        # --- Add Commit Logs if there are new commits ---
        if commit_logs:
            embed.add_field(
                name="Recent Commits",
                value=commit_logs[:1024],  # prevent field from exceeding Discord limit
                inline=False
            )

        # --- Time Handling ---
        now_utc = datetime.now(timezone.utc)
        unix_ts = int(now_utc.timestamp())
        today_utc = datetime.now(timezone.utc).date()
        date_label = "Today" if now_utc.date() == today_utc else now_utc.strftime("%B %d, %Y")

        embed.set_footer(text=f"{date_label} at your local time • <t:{unix_ts}:t> | <t:{unix_ts}:R>")

        await channel.send(embed=embed)

    @staticmethod
    def restart_bot():
        """Restarts the bot using the current Python interpreter."""
        os.execv(sys.executable, [sys.executable] + sys.argv)

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

        # Restart logic only if updated successfully
        if "already up to date." in git_response.lower():
            return
        elif "error" in git_response.lower() or "conflict" in git_response.lower():
            return
        else:
            print("[ SYSTEM ] Rebooting bot...")
            self.restart_bot()

async def setup(bot: commands.Bot):
    """Adds the Updater cog to the bot."""
    await bot.add_cog(Updater(bot))
