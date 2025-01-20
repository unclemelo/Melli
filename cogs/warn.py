import discord
import json
import os
from discord import app_commands
from discord.ext import commands

WARN_FILE = 'data/warns.json'  # File to store warnings

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.warnings = self.load_warnings()

    def load_warnings(self):
        """Load warnings from the file."""
        if os.path.exists(WARN_FILE):
            with open(WARN_FILE, 'r') as file:
                return json.load(file)
        return {}

    def save_warnings(self):
        """Save warnings to the file."""
        with open(WARN_FILE, 'w') as file:
            json.dump(self.warnings, file, indent=4)

    @app_commands.command(name="warn", description="Warn a user and log the reason.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a user and log the reason, guild-specific."""
        if member.bot:
            await interaction.response.send_message("You cannot warn a bot.")
            return

        # Initialize guild and user warnings if not present
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []

        # Add the warning
        self.warnings[guild_id][user_id].append({
            "reason": reason,
            "moderator": str(interaction.user),
            "timestamp": interaction.message.created_at.isoformat()
        })
        self.save_warnings()

        # Send confirmation
        embed = Embed(title="User Warned", color=discord.Color.yellow())
        embed.add_field(name="User", value=f"{member.mention}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=str(interaction.user), inline=True)
        embed.set_footer(text="Use the 'warnings' command to view all warnings.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="Display all warnings for a user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Display all warnings for a user, guild-specific."""
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.warnings and user_id in self.warnings[guild_id] and self.warnings[guild_id][user_id]:
            embed = Embed(title=f"Warnings for {member.display_name}", color=discord.Color.orange())
            for i, warn in enumerate(self.warnings[guild_id][user_id], start=1):
                embed.add_field(
                    name=f"Warning {i}",
                    value=f"**Reason:** {warn['reason']}\n"
                          f"**Moderator:** {warn['moderator']}\n"
                          f"**Date:** {warn['timestamp']}",
                    inline=False
                )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{member.mention} has no warnings in this server.")

    @app_commands.command(name="delwarn", description="Delete a specific warning for a user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delwarn(self, interaction: discord.Interaction, member: discord.Member, warn_index: int):
        """Delete a specific warning for a user, guild-specific."""
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.warnings and user_id in self.warnings[guild_id] and 0 < warn_index <= len(self.warnings[guild_id][user_id]):
            removed_warn = self.warnings[guild_id][user_id].pop(warn_index - 1)
            self.save_warnings()

            embed = Embed(title="Warning Removed", color=discord.Color.green())
            embed.add_field(name="User", value=f"{member.mention}", inline=True)
            embed.add_field(name="Removed Reason", value=removed_warn['reason'], inline=True)
            embed.add_field(name="Moderator", value=removed_warn['moderator'], inline=True)
            await interaction.response.send_message(embed=embed)

            # Remove user if no warnings are left
            if not self.warnings[guild_id][user_id]:
                del self.warnings[guild_id][user_id]
                if not self.warnings[guild_id]:  # Remove guild if no warnings left
                    del self.warnings[guild_id]
                self.save_warnings()
        else:
            await interaction.response.send_message(f"Invalid warning index or {member.mention} has no warnings in this server.")

    @app_commands.command(name="clearwarns", description="Clear all warnings for a user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
        """Clear all warnings for a user, guild-specific."""
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            del self.warnings[guild_id][user_id]
            # Remove guild if no warnings left
            if not self.warnings[guild_id]:
                del self.warnings[guild_id]
            self.save_warnings()
            await interaction.response.send_message(f"Cleared all warnings for {member.mention} in this server.")
        else:
            await interaction.response.send_message(f"{member.mention} has no warnings in this server.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))
