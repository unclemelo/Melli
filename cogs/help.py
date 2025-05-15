import discord
import json
from discord import app_commands
from discord.ext import commands
from util.command_checks import command_enabled

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def build_embed(self, category: str) -> discord.Embed:
        embed = discord.Embed(
            title="📖 • Melli's Commands & Features",
            description="Use `/add_melli` to see who helped build Melli!\n[🛠 Join the Support Server](https://discord.gg/r2q6gNp9t3)",
            color=discord.Color.magenta()
        )

        if category in ("all", "utility"):
            embed.add_field(
                name="╭─💡 Utility Commands ───────────────╮",
                value=(
                    "• `/supporters` — Show top boosters of the support server.\n"
                    "• `/profile [user]` — View your profile or another user's profile.\n"
                    "• `/add_melli` — Invite Melli & view credits.\n"
                    "• `/command_config` — Enable or disable commands for this server."
                ),
                inline=False
            )

        if category in ("all", "moderation"):
            embed.add_field(
                name="╭─📌 Moderation Tools ───────────────╮",
                value=(
                    "• `/mute <user> <duration> [reason]` — Temporarily mute a user.\n"
                    "• `/unmute <user>` — Remove a timeout from a user.\n"
                    "• `/clear <amount>` — Delete messages in bulk.\n"
                    "• `/warn <user> <reason>` — Warn a member.\n"
                    "• `/warnings <user>` — Show warnings for a user.\n"
                    "• `/delwarn <warning_id>` — Delete a specific warning.\n"
                    "• `/clearwarns <user>` — Clear all warnings for a user.\n"
                    "• `/kick <user> [reason]` — Kick a member.\n"
                    "• `/ban <user> [reason]` — Ban a member.\n"
                    "• `/unban <user>` — Unban a previously banned user.\n"
                    "• `/setup` — Interactive AutoMod setup wizard.\n"
                    "• `/forceupdate` — Refresh AutoMod rules immediately."
                ),
                inline=False
            )

        if category in ("all", "vc"):
            embed.add_field(
                name="╭─🔊 VC Tools ───────────────────────╮",
                value=(
                    "• `/bump <user> <target_vc>` — Move a user to another voice channel.\n"
                    "• `/vc_mute <user>` — Server mute a user in voice chat.\n"
                    "• `/vc_unmute <user>` — Unmute a user in voice chat.\n"
                    "• `/deafen <user>` — Server deafen a user in voice chat.\n"
                    "• `/undeafen <user>` — Remove deafening from a user.\n"
                    "• `/kickvc <user>` — Disconnect a user from voice chat."
                ),
                inline=False
            )

        if category in ("all", "fun"):
            embed.add_field(
                name="╭─🎉 Fun & Extras ─────────────────╮",
                value=(
                    "• `/knockout <user>` — Timeout a user dramatically!\n"
                    "• `/revive <user>` — Bring back a timed-out user.\n"
                    "• `/prank <user>` — Harmlessly prank a user.\n"
                    "• `/chaos` — Temporarily unleash chaotic actions."
                ),
                inline=False
            )

        embed.set_footer(text="Need more help? Join the support server or ping a mod!")
        return embed

    @app_commands.command(name="help", description="Get a list of available commands")
    @app_commands.describe(category="Pick a category to see commands from")
    @app_commands.choices(category=[
        app_commands.Choice(name="All", value="all"),
        app_commands.Choice(name="Moderation", value="moderation"),
        app_commands.Choice(name="Utility", value="utility"),
        app_commands.Choice(name="VC Tools", value="vc"),
        app_commands.Choice(name="Fun", value="fun"),
    ])
    @command_enabled()
    async def help(self, interaction: discord.Interaction, category: app_commands.Choice[str] = None):
        selected_category = category.value if category else "all"
        embed = self.build_embed(selected_category)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
