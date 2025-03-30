import discord
import os
import sys
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from functools import wraps

# Developer IDs
devs = {667032667732312115, 954135885392252940, 1186435491252404384}

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

class System(commands.Cog):
    """Cog for managing system-level commands like shutting down the bot."""
    
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
            print(f"- [ ERROR ] {error}")
            raise error

    @app_commands.command(name="shutdown", description="Developer Only")
    @is_dev()
    async def shutdown_cmd(self, interaction: discord.Interaction):
        """Command to shut down the bot."""
        embed = discord.Embed(
            title="Shutting Down `Melli`...",
            description="The bot is shutting down.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print("[ SYSTEM ] Bot shutting down...")
        await self.bot.close()

async def setup(bot: commands.Bot):
    """Adds the System cog to the bot."""
    await bot.add_cog(System(bot))
