import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from util.command_checks import is_command_enabled

class Mute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Temporarily mutes a user using Discord's timeout feature.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_cmd(self, interaction: discord.Interaction, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "mute"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
        try:
            # Apply timeout
            await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes), reason=reason)
            
            embed = discord.Embed(
                title=f"🤐 {member.name} has been muted!",
                description=f"Reason: {reason}\nDuration: {minutes} minutes.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Hmm... couldn't mute {member.name}. Did they dodge the timeout? 🕵️\nError: {str(e)}")

    @app_commands.command(name="unmute", description="Removes a user's mute (timeout).")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute_cmd(self, interaction: discord.Interaction, member: discord.Member):
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "unmute"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
        try:
            # Remove timeout
            await member.timeout(discord.utils.utcnow() + timedelta(minutes=0))
            
            embed = discord.Embed(
                title=f"🔊 {member.name} has been unmuted!",
                description="They can now speak freely... for better or worse. 🤔",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Couldn't unmute {member.name}. Are they already unmuted? 🤷\nError: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Mute(bot))

