import discord
import subprocess
import os
import sys
import asyncio
import traceback
from datetime import datetime
from discord import app_commands
from discord.ext import commands

GITHUB_REPO = "https://github.com/unclemelo/Melli"
DEV_ROLE_ID = 1434074860681822259

class Updater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------------------------------
    # Helper: Check for developer role
    # -------------------------------------------------
    async def _is_dev(self, interaction: discord.Interaction):
        if DEV_ROLE_ID == 0:
            return True
        return any(role.id == DEV_ROLE_ID for role in interaction.user.roles)

    # -------------------------------------------------
    # Helper: Send error embed
    # -------------------------------------------------
    async def send_error_embed(self, interaction: discord.Interaction, error: Exception, command_name: str):
        """Sends an informative error message when a command fails."""
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        embed = discord.Embed(
            title=f"⚠️ Error in `{command_name}`",
            description=f"An error occurred while running the `{command_name}` command.",
            color=discord.Color.red()
        )
        embed.add_field(name="Error Type", value=f"`{type(error).__name__}`", inline=True)
        embed.add_field(name="Error Message", value=f"```{str(error)[:500]}```", inline=False)
        embed.set_footer(text="Check console for traceback details.")
        await interaction.followup.send(embed=embed)
        print(f"[Updater Error] {command_name} failed:\n{tb}")

    # -------------------------------------------------
    # /update - main update + restart
    # -------------------------------------------------
    @app_commands.command(name="update", description="Pull updates from GitHub and restart the bot.")
    async def update_bot(self, interaction: discord.Interaction):
        if not await self._is_dev(interaction):
            return await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)

        await interaction.response.defer(thinking=True)
        try:
            process = subprocess.run(["git", "pull"], capture_output=True, text=True)
            output = process.stdout.strip() or process.stderr.strip()

            if "Already up to date" in output:
                return await interaction.followup.send("✅ No updates available. The bot is already up to date.")

            embed = discord.Embed(
                title="🔁 Bot Updated",
                description="Successfully pulled updates from GitHub and restarting...",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="GitHub Status", value=f"Updates applied successfully. [View on GitHub]({GITHUB_REPO})", inline=False)

            try:
                commits = subprocess.run(["git", "log", "-5", "--pretty=format:• %s (%an)"], capture_output=True, text=True)
                commit_list = commits.stdout.strip()
                embed.add_field(name="Recent Commits", value=f"```\n{commit_list}\n```", inline=False)
            except Exception as e:
                embed.add_field(name="Recent Commits", value=f"Could not retrieve commit log.\nError: {e}", inline=False)

            now = int(datetime.now().timestamp())
            embed.set_footer(text=f"Today at your local time • <t:{now}:t> | <t:{now}:R>")
            await interaction.followup.send(embed=embed)

            await asyncio.sleep(3)
            os.execv(sys.executable, ["python"] + sys.argv)

        except Exception as e:
            await self.send_error_embed(interaction, e, "update")

    # -------------------------------------------------
    # /update commits
    # -------------------------------------------------
    @app_commands.command(name="update_commits", description="View the most recent GitHub commits.")
    async def recent_commits(self, interaction: discord.Interaction):
        if not await self._is_dev(interaction):
            return await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)

        await interaction.response.defer()
        try:
            process = subprocess.run(["git", "log", "-5", "--pretty=format:• %s (%an)"], capture_output=True, text=True)
            commits = process.stdout.strip() or "No commits found."
            embed = discord.Embed(title="📝 Recent Commits", description=f"```\n{commits}\n```", color=discord.Color.blurple())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await self.send_error_embed(interaction, e, "update_commits")

    # -------------------------------------------------
    # /update test
    # -------------------------------------------------
    @app_commands.command(name="update_test", description="Simulate an update pull without restarting.")
    async def test_update(self, interaction: discord.Interaction):
        if not await self._is_dev(interaction):
            return await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)

        await interaction.response.defer()
        try:
            process = subprocess.run(["git", "fetch"], capture_output=True, text=True)
            ahead_check = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
            embed = discord.Embed(title="🧪 Update Test", color=discord.Color.orange())
            embed.add_field(name="Git Fetch Output", value=f"```\n{process.stdout.strip()[:500]}\n```", inline=False)
            embed.add_field(name="Status", value=f"```\n{ahead_check.stdout.strip()[:500]}\n```", inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await self.send_error_embed(interaction, e, "update_test")

    # -------------------------------------------------
    # /update reload
    # -------------------------------------------------
    @app_commands.command(name="update_reload", description="Reload all cogs without a full restart.")
    async def reload_cogs(self, interaction: discord.Interaction):
        if not await self._is_dev(interaction):
            return await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)

        try:
            reloaded = []
            failed = []
            for ext in list(self.bot.extensions.keys()):
                try:
                    await self.bot.reload_extension(ext)
                    reloaded.append(ext)
                except Exception as e:
                    failed.append(f"{ext}: {e}")
                    print(f"Failed to reload {ext}: {e}")

            embed = discord.Embed(title="♻️ Reloaded Cogs", color=discord.Color.green())
            embed.add_field(name="Reloaded", value=f"```\n{chr(10).join(reloaded) or 'None'}\n```", inline=False)
            if failed:
                embed.add_field(name="Failed", value=f"```\n{chr(10).join(failed)[:1000]}\n```", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await self.send_error_embed(interaction, e, "update_reload")

    # -------------------------------------------------
    # /update status
    # -------------------------------------------------
    @app_commands.command(name="update_status", description="Show current version, branch, and uptime.")
    async def update_status(self, interaction: discord.Interaction):
        try:
            branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
            commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()

            embed = discord.Embed(title="📊 Bot Status", color=discord.Color.blue())
            embed.add_field(name="Branch", value=branch or "Unknown")
            embed.add_field(name="Commit", value=commit or "Unknown")
            embed.add_field(name="GitHub", value=f"[View Repository]({GITHUB_REPO})", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await self.send_error_embed(interaction, e, "update_status")

    # -------------------------------------------------
    # /update info
    # -------------------------------------------------
    @app_commands.command(name="update_info", description="Display bot update info and recent activity.")
    async def update_info(self, interaction: discord.Interaction):
        try:
            process = subprocess.run(["git", "log", "-3", "--pretty=format:• %s (%an)"], capture_output=True, text=True)
            embed = discord.Embed(
                title="ℹ️ Bot Update Info",
                description="Quick summary of recent updates and version info.",
                color=discord.Color.purple()
            )
            embed.add_field(name="Current Commit", value=subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip())
            embed.add_field(name="Recent Commits", value=f"```\n{process.stdout.strip()}\n```", inline=False)
            embed.add_field(name="GitHub Repo", value=f"[View Repository]({GITHUB_REPO})", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await self.send_error_embed(interaction, e, "update_info")


async def setup(bot):
    await bot.add_cog(Updater(bot))
