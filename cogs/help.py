import discord
import json
from discord import app_commands
from discord.ext import commands
from util.command_checks import is_command_enabled

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
                    "• `/profile` — View your profile stored by Melli.\n"
                    "• `/add_melli` — Invite Melli & view credits."
                ),
                inline=False
            )

        if category in ("all", "moderation"):
            embed.add_field(
                name="╭─📌 Moderation Tools ───────────────╮",
                value=(
                    "• `/mute` — Temporarily mute a user.\n"
                    "• `/unmute` — Remove a timeout.\n"
                    "• `/clear` — Delete messages in bulk.\n"
                    "• `/warn` — Warn a member.\n"
                    "• `/warnings` — Show warnings for a user.\n"
                    "• `/delwarn` — Delete a specific warning.\n"
                    "• `/clearwarns` — Clear all warnings.\n"
                    "• `/kick` — Kick a member.\n"
                    "• `/ban` — Ban a member.\n"
                    "• `/unban` — Unban someone.\n"
                    "• `/setup` — Interactive AutoMod setup.\n"
                    "• `/forceupdate` — Refresh AutoMod rules."
                ),
                inline=False
            )

        if category in ("all", "vc"):
            embed.add_field(
                name="╭─🔊 VC Tools ───────────────────────╮",
                value=(
                    "• `/bump` — Move a user to another VC.\n"
                    "• `/vc_mute` — Server mute a user in VC.\n"
                    "• `/vc_unmute` — Unmute a user in VC.\n"
                    "• `/deafen` — Server deafen a user.\n"
                    "• `/undeafen` — Remove deafening.\n"
                    "• `/kickvc` — Kick someone from VC."
                ),
                inline=False
            )

        if category in ("all", "fun"):
            embed.add_field(
                name="╭─🎉 Fun & Extras ─────────────────╮",
                value=(
                    "• `/knockout` — Timeout a user dramatically!\n"
                    "• `/revive` — Bring back a timed-out user.\n"
                    "• `/prank` — Harmlessly prank a user.\n"
                    "• `/chaos` — Temporarily unleash chaos."
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
    async def help(self, interaction: discord.Interaction, category: app_commands.Choice[str] = None):
        if not is_command_enabled(interaction.guild.id, "help"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return

        selected_category = category.value if category else "all"
        embed = self.build_embed(selected_category)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))