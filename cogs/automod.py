import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup_automod", description="Automatically sets up AutoMod rules for the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_automod(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Automatically sets up AutoMod rules for the server with predefined configurations.
        """
        try:
            guild = interaction.guild
            if not guild:
                await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
                return

            blocked_links_regex = [
                r"(?:https?://?)?(\S*@)?[\\a-z0-9_\-\.\%]*[a-z0-9_\-%]+(\.|%2e)[a-z(%[a-z0-9])]{2,}",
                r"(?:https?://)?(?:www.|ptb.|canary.)?(?:dsc\.gg|invite\.gg|discord\.link|(?:discord\.(?:gg|io|me|li|id))|disboard\.org|discord(?:app)?\.(?:com|gg)/(?:invite|servers))/[a-z0-9-_]+",
                r"[a-z0-9_\-\.\+]+@[a-z0-9_\-\.]*[a-z0-9_\-]+\.[a-z]{2,}",
                r"\[.*[a-z0-9_\-]+\.[a-z]{2,}[\/]?.*\]\(<?(?:https?://)?[a-z0-9_\-\.]*[a-z0-9_\-]+\.[a-z]{2,}.*>?\)"
            ]

            blocked_text_regex = [
                r"^(> )?#{1,3}\s.*$",
                r"(?m)^-#\s.*$",
                r"(?s)(?i)((<a?:[a-z_0-9]+:[0-9]+>|\p{Extended_Pictographic}|[\u{1F1E6}-\u{1F1FF}]|[0-9#\*]\u{fe0f}).*){4,}",
                r"\p{M}{3,}"
            ]

            allowed_links = [
                "*://c.tenor.com/*", "*://cdn.discordapp.com/*", "*://imgflip.com/*", "*://media.discordapp.net/*", "*://on.soundcloud.com/*", "*://open.spotify.com/*", "*://tenor.com/*", "*://treeben77.github.io/*", "*://www.bilibili.com/*", "*://www.youtube.com/*", "*://youtu.be/*", "*://youtube.com/*", "*.go*", "*.js*", "*.py*", "poly.ai"
            ]

            # Create AutoMod Rule: Block Harmful Links
            rule_1 = await guild.create_automod_rule(
                name="Blocked Links",
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(
                    type=discord.AutoModRuleTriggerType.keyword,
                    regex_patterns=blocked_links_regex,
                    allow_list=allowed_links
                ),
                actions=[
                    discord.AutoModRuleAction(
                        channel_id=channel.id,
                        type=discord.AutoModRuleActionType.block_message
                    ), 
                    discord.AutoModRuleAction(
                        channel_id=channel.id
                    )],
                enabled=True,
                reason="Prevent harmful or spam links."
            )

            # Create AutoMod Rule: Block Spam Text
            rule_2 = await guild.create_automod_rule(
                name="Blocked Text",
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(
                    type=discord.AutoModRuleTriggerType.keyword,
                    regex_patterns=blocked_text_regex
                ),
                actions=[
                    discord.AutoModRuleAction(
                        channel_id=channel.id,
                        type=discord.AutoModRuleActionType.block_message
                    ), 
                    discord.AutoModRuleAction(
                        channel_id=channel.id
                    )],
                enabled=True,
                reason="Prevent spam or malicious text."
            )

            embed = discord.Embed(title="AutoMod setup complete!", description=f"Created rules:\n- **{rule_1.name}**\n- **{rule_2.name}**", color=0x03fcb6)

            await interaction.response.send_message(
                embed=embed
            )
        except Exception as e:
            print(f"Error in AutoMod setup: {e}")
            await interaction.response.send_message("An error occurred. Please contact an administrator.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))