import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from util.command_checks import is_command_enabled

class Clear(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Clears a number of messages.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_cmd(self, interaction: discord.Interaction, amount: int):
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "clear"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
        try:
            await interaction.response.send_message(f"🧹 Poof! Cleared {amount} messages. The chat looks spotless now!", ephemeral=True)
            try:
                await interaction.channel.purge(limit=amount)
            except Exception as e:
                print(f"[ERROR] {e}")
                pass
        except Exception as e:
            await interaction.response.send_message(f"Yikes! Couldn't clear messages. Is the vacuum broken? 🧼\nError: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Clear(bot))

