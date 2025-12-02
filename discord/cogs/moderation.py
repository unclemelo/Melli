import discord
import json
import aiofiles
import os
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from util.command_checks import command_enabled

WARN_FILE = 'data/warns.json'


class Moderation(commands.Cog):
    """🛠️ Melli's Moderation Tools"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.warnings = self.load_warnings_sync()

    # ───────────────────────────────────────────────
    # Utility methods
    # ───────────────────────────────────────────────
    def load_warnings_sync(self):
        """Load warnings synchronously on startup."""
        if os.path.exists(WARN_FILE):
            with open(WARN_FILE, 'r', encoding='utf-8') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        return {}

    async def save_warnings(self):
        """Save warnings asynchronously."""
        async with aiofiles.open(WARN_FILE, 'w', encoding='utf-8') as file:
            await file.write(json.dumps(self.warnings, indent=4))

    def ensure_guild_user(self, guild_id: str, user_id: str):
        """Ensure guild and user warning dicts exist."""
        self.warnings.setdefault(guild_id, {}).setdefault(user_id, [])

    def build_embed(self, title: str, description: str = None, color: discord.Color = discord.Color.blurple()):
        """Return a nicely formatted embed."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Melli Moderation System")
        return embed

    # ───────────────────────────────────────────────
    # Commands
    # ───────────────────────────────────────────────

    @app_commands.command(name="mute", description="Temporarily mute a user using Discord's timeout system.")
    @app_commands.checks.has_permissions(manage_nicknames=True)

    async def mute_cmd(self, interaction: discord.Interaction, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't mute someone with an equal or higher role.", ephemeral=True)

        try:
            await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes), reason=reason)
            embed = self.build_embed(
                f"🤐 {member.display_name} has been muted!",
                f"**Reason:** {reason}\n**Duration:** {minutes} minutes.",
                discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to mute {member.mention}.\n`{e}`", ephemeral=True)

    @app_commands.command(name="unmute", description="Remove a user's timeout.")
    @app_commands.checks.has_permissions(manage_nicknames=True)

    async def unmute_cmd(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.timeout(None)
            embed = self.build_embed(
                f"🔊 {member.display_name} has been unmuted!",
                "They can now speak freely again.",
                discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unmute {member.mention}.\n`{e}`", ephemeral=True)

    @app_commands.command(name="clear", description="Clear a number of messages from the current channel.")
    @app_commands.checks.has_permissions(manage_messages=True)

    async def clear_cmd(self, interaction: discord.Interaction, amount: int):
        await interaction.response.send_message(f"🧹 Clearing {amount} messages...", ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Cleared {len(deleted)} messages!", ephemeral=True)

    @app_commands.command(name="warn", description="Warn a user and log it.")
    @app_commands.checks.has_permissions(manage_messages=True)

    async def warn_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        if member.bot:
            return await interaction.response.send_message("You cannot warn a bot.", ephemeral=True)

        guild_id, user_id = str(interaction.guild.id), str(member.id)
        self.ensure_guild_user(guild_id, user_id)

        self.warnings[guild_id][user_id].append({
            "reason": reason,
            "moderator": str(interaction.user),
            "timestamp": discord.utils.utcnow().isoformat()
        })
        await self.save_warnings()

        embed = self.build_embed("⚠️ User Warned", color=discord.Color.yellow())
        embed.add_field(name="User", value=member.mention)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="View all warnings for a user.")
    @app_commands.checks.has_permissions(manage_messages=True)

    async def warnings_cmd(self, interaction: discord.Interaction, member: discord.Member):
        guild_id, user_id = str(interaction.guild.id), str(member.id)
        warns = self.warnings.get(guild_id, {}).get(user_id, [])

        if not warns:
            return await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)

        embed = self.build_embed(f"⚠️ Warnings for {member.display_name}", color=discord.Color.orange())
        for i, warn in enumerate(warns, 1):
            embed.add_field(
                name=f"#{i} — {warn['timestamp'][:10]}",
                value=f"**Reason:** {warn['reason']}\n**Moderator:** {warn['moderator']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delwarn", description="Delete a specific warning for a user.")
    @app_commands.checks.has_permissions(manage_messages=True)

    async def delwarn_cmd(self, interaction: discord.Interaction, member: discord.Member, warn_index: int):
        guild_id, user_id = str(interaction.guild.id), str(member.id)
        warns = self.warnings.get(guild_id, {}).get(user_id, [])

        if not warns or not (0 < warn_index <= len(warns)):
            return await interaction.response.send_message(f"Invalid index or no warnings for {member.mention}.", ephemeral=True)

        removed = warns.pop(warn_index - 1)
        if not warns:
            self.warnings[guild_id].pop(user_id)
            if not self.warnings[guild_id]:
                self.warnings.pop(guild_id)

        await self.save_warnings()

        embed = self.build_embed("✅ Warning Removed", color=discord.Color.green())
        embed.add_field(name="User", value=member.mention)
        embed.add_field(name="Removed Reason", value=removed['reason'], inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarns", description="Clear all warnings for a user.")
    @app_commands.checks.has_permissions(manage_messages=True)

    async def clearwarns_cmd(self, interaction: discord.Interaction, member: discord.Member):
        guild_id, user_id = str(interaction.guild.id), str(member.id)
        if guild_id not in self.warnings or user_id not in self.warnings[guild_id]:
            return await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)

        del self.warnings[guild_id][user_id]
        if not self.warnings[guild_id]:
            del self.warnings[guild_id]
        await self.save_warnings()

        await interaction.response.send_message(f"✅ Cleared all warnings for {member.mention}.")

    @app_commands.command(name="kick", description="Kick a user from the server.")
    @app_commands.checks.has_permissions(kick_members=True)

    async def kick_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't kick someone with an equal or higher role.", ephemeral=True)

        try:
            await member.kick(reason=reason)
            embed = self.build_embed(
                f"🥾 {member.display_name} has been kicked!",
                f"**Reason:** {reason}",
                discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to kick {member.mention}.\n`{e}`", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.checks.has_permissions(ban_members=True)

    async def ban_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't ban someone with an equal or higher role.", ephemeral=True)

        try:
            await member.ban(reason=reason)
            embed = self.build_embed(
                f"🔨 {member.display_name} was banned!",
                f"**Reason:** {reason}",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to ban {member.mention}.\n`{e}`", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user by their ID.")
    @app_commands.checks.has_permissions(ban_members=True)

    async def unban_cmd(self, interaction: discord.Interaction, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            embed = self.build_embed(
                f"✨ {user.name} was unbanned!",
                "Let's hope they behave this time.",
                discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Couldn't unban that user.\n`{e}`", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
