import discord
from discord import app_commands
from discord.ext import commands
from util.command_checks import command_enabled

class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def build_embed(self, category: str) -> discord.Embed:
        embed = discord.Embed(
            title="📖 • Melli's Commands & Features",
            description="Use `/add_melli` to see who helped build Melli!\n[🛠 Join the Support Server](https://discord.gg/r2q6gNp9t3)",
            color=discord.Color.magenta()
        )

        if category in ("all", "utility"):
            embed.add_field(
                name="💡 Utility Commands",
                value=(
                    "• `/profile [user]` — View your profile or another user's profile.\n"
                ),
                inline=False
            )

        if category in ("all", "moderation"):
            embed.add_field(
                name="📌 Moderation Tools",
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
                ),
                inline=False
            )

        if category in ("all", "automod"):
            embed.add_field(
                name="🛡️ AutoMod Commands",
                value=(
                    "• `/setup` — Interactive AutoMod setup wizard.\n"
                    "• `/forceupdate` — Refresh AutoMod rules immediately.\n"
                    "• `/show_config` — Lets you see the current AutoMod settings in a neat embed.\n"
                    "• `/clear_config` — Wipes your AutoMod settings for the guild.\n"
                    "• `/set_log_channel` — Lets you pick the log channel explicitly, stored in temp data for now."
                ),
                inline=False
            )

        if category in ("all", "vc"):
            embed.add_field(
                name="🔊 VC Tools",
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
                name="🎉 Fun & Extras",
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
        app_commands.Choice(name="AutoMod", value="automod"),
        app_commands.Choice(name="VC Tools", value="vc"),
        app_commands.Choice(name="Fun", value="fun"),
    ])
    @command_enabled()
    async def help(self, interaction: discord.Interaction, category: app_commands.Choice[str] = None):
        selected_category = category.value if category else "all"
        embed = self.build_embed(selected_category)
        view = HelpView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if self.bot.user in message.mentions:
            embed = discord.Embed(
                title="<:vwv:1323527766011809873> Hey there!",
                description=(
                    "I'm **Melli**, your moderation, utility, and fun assistant.\n\n"
                    "Use the **`/help`** command to see everything I can do for you!\n"
                    "[🛠 Support Server](https://discord.gg/r2q6gNp9t3) <:embarrassed:1323530963074158642>"
                ),
                color=discord.Color.magenta()
            )
            embed.set_footer(text="Thanks for mentioning me")
            try:
                await message.reply(embed=embed, mention_author=False)
            except discord.Forbidden:
                pass  # Bot can't send messages here


class HelpView(discord.ui.View):
    def __init__(self, cog: HelpCommand):
        super().__init__(timeout=60)
        self.cog = cog

    @discord.ui.select(
        placeholder="Select a command category...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="All", value="all", emoji="📖"),
            discord.SelectOption(label="Moderation", value="moderation", emoji="📌"),
            discord.SelectOption(label="Utility", value="utility", emoji="💡"),
            discord.SelectOption(label="AutoMod", value="automod", emoji="🛡️"),
            discord.SelectOption(label="VC Tools", value="vc", emoji="🔊"),
            discord.SelectOption(label="Fun", value="fun", emoji="🎉"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        embed = self.cog.build_embed(value)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        # Disable the select when view times out
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))
