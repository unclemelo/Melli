import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded automod.py")

    @app_commands.command(name="setup_automod", description="Automatically sets up AutoMod rules for the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_automod(self, interaction: discord.Interaction):
        """
        Automatically sets up AutoMod rules for the server with predefined configurations.
        """
        try:
            guild = interaction.guild

            if not guild:
                await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
                return

            # Rule 1: Block Harmful Links (with regex and exceptions)
            blocked_links_regex = [
                r"(?:https?://?)?(\S*@)?[\\a-z0-9_\-\.\%]*[a-z0-9_\-%]+(\.|%2e)[a-z(%[a-z0-9])]{2,}",
                r"(?:https?://)?(?:www.|ptb.|canary.)?(?:dsc\.gg|invite\.gg|discord\.link|(?:discord\.(?:gg|io|me|li|id))|disboard\.org|discord(?:app)?\.(?:com|gg)/(?:invite|servers))/[a-z0-9-_]+",
                r"[a-z0-9_\-\.\+]+@[a-z0-9_\-\.]*[a-z0-9_\-]+\.[a-z]{2,}",
                r"\[.*[a-z0-9_\-]+\.[a-z]{2,}[\/]?.*\]\(<?(?:https?://)?[a-z0-9_\-\.]*[a-z0-9_\-]+\.[a-z]{2,}.*>?\)"
            ]
            allowed_links = [
                "*://tenor.com/*", "*://cdn.discordapp.com/*", "*://imgflip.com/*",
                "*://media.discordapp.net/*", "*://on.soundcloud.com/*",
                "*://open.spotify.com/*", "*://youtube.com/*"
            ]

            await guild.create_automod_rule(
                name="Blocked Links",
                trigger=discord.AutoModTrigger(
                    type=discord.AutoModRuleTriggerType.keyword,
                    regex_patterns=blocked_links_regex,
                    allow_list=allowed_links
                ),
                actions=[
                    discord.AutoModAction(
                        type=discord.AutoModRuleActionType.block_message
                    )
                ]
            )

            # Rule 2: Blocked Text (with regex)
            blocked_text_regex = [
                r"^(> )?#{1,3}\s.*$",
                r"(?m)^-#\s.*$",
                r"(?s)(?i)((<a?:[a-z_0-9]+:[0-9]+>|\p{Extended_Pictographic}|[\u{1F1E6}-\u{1F1FF}]|[0-9#\*]\u{fe0f}).*){4,}",
                r"\p{M}{3,}"
            ]

            await guild.create_automod_rule(
                name="Blocked Text",
                trigger=discord.AutoModTrigger(
                    type=discord.AutoModRuleTriggerType.keyword,
                    regex_patterns=blocked_text_regex
                ),
                actions=[
                    discord.AutoModAction(
                        type=discord.AutoModRuleActionType.block_message
                    )
                ]
            )

            await interaction.response.send_message(
                "AutoMod setup complete! Rules for 'Blocked Links' and 'Blocked Text' have been created."
            )

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
