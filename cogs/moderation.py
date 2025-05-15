import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from util.command_checks import command_enabled

WARN_FILE = 'data/warns.json'

class Moderation(commands.Cog):
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
    
    @app_commands.command(name="mute", description="Temporarily mutes a user using Discord's timeout feature.")
    @app_commands.checks.has_permissions(moderate_members=True)
    @command_enabled()
    async def mute_cmd(self, interaction: discord.Interaction, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
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
    @command_enabled()
    async def unmute_cmd(self, interaction: discord.Interaction, member: discord.Member):
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
    
    @app_commands.command(name="clear", description="Clears a number of messages.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @command_enabled()
    async def clear_cmd(self, interaction: discord.Interaction, amount: int):
        try:
            await interaction.response.send_message(f"🧹 Poof! Cleared {amount} messages. The chat looks spotless now!", ephemeral=True)
            try:
                await interaction.channel.purge(limit=amount)
            except Exception as e:
                print(f"[ERROR] {e}")
                pass
        except Exception as e:
            await interaction.response.send_message(f"Yikes! Couldn't clear messages. Is the vacuum broken? 🧼\nError: {str(e)}")
    
    @app_commands.command(name="warn", description="Warn a user and log the reason.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @command_enabled()
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
            "timestamp": discord.utils.utcnow().isoformat()
        })
        self.save_warnings()

        # Send confirmation
        embed = discord.Embed(title="User Warned", color=discord.Color.yellow())
        embed.add_field(name="User", value=f"{member.mention}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=str(interaction.user), inline=True)
        embed.set_footer(text="Use the 'warnings' command to view all warnings.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="Display all warnings for a user.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @command_enabled()
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Display all warnings for a user, guild-specific."""
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.warnings and user_id in self.warnings[guild_id] and self.warnings[guild_id][user_id]:
            embed = discord.Embed(title=f"Warnings for {member.display_name}", color=discord.Color.orange())
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
    @command_enabled()
    async def delwarn(self, interaction: discord.Interaction, member: discord.Member, warn_index: int):
        """Delete a specific warning for a user, guild-specific."""
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.warnings and user_id in self.warnings[guild_id] and 0 < warn_index <= len(self.warnings[guild_id][user_id]):
            removed_warn = self.warnings[guild_id][user_id].pop(warn_index - 1)
            self.save_warnings()

            embed = discord.Embed(title="Warning Removed", color=discord.Color.green())
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
    @command_enabled()
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

    @app_commands.command(name="kick", description="Kicks a user.")
    @app_commands.checks.has_permissions(kick_members=True)
    @command_enabled()
    async def kick_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        try:
            embed = discord.Embed(
                title=f"🥾 **{member.name} was yeeted out of the server!**",
                description=f"Reason: {reason}\nFly safe, traveler. 🚀",
                color=discord.Color.orange()
            )
            await member.kick(reason=reason)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Oops! Couldn't kick {member.name}. Maybe they bribed the mods? 🧐\nError: {str(e)}")
    
    @app_commands.command(name="ban", description="Bans a user.")
    @app_commands.checks.has_permissions(ban_members=True)
    @command_enabled()
    async def ban_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        try:
            embed = discord.Embed(
                title=f"🔨 **{member.name} was struck by the Melon Hammer!**",
                description=f"Reason: {reason}\nThey had it coming!",
                color=discord.Color.red()
            )
            await member.ban(reason=reason)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Oops! Couldn't ban {member.name}. Did they dodge the hammer? 😳\nError: {str(e)}")

    @app_commands.command(name="unban", description="Unbans a user.")
    @app_commands.checks.has_permissions(ban_members=True)
    @command_enabled()
    async def unban_cmd(self, interaction: discord.Interaction, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title=f"✨ {user.name} is free from ban jail!",
                description="Let's hope they behave this time. 🤔",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Hmm... couldn't unban that user. Are you sure they're banned? 😅\nError: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))