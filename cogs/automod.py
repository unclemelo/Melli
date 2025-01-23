import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore
import json
import os

CONFIG_FILE = "data/AM_conf.json"

from functools import wraps

# Developer IDs
devs = [667032667732312115, 954135885392252940, 1186435491252404384]

def is_dev():
    """A decorator to restrict commands to developers."""
    def predicate(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if interaction.user.id in self.devs:
                return await func(self, interaction, *args, **kwargs)
            else:
                await interaction.response.send_message(
                    "Sorry, this command is restricted to developers.", ephemeral=True
                )
        return wrapper
    return predicate

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load_config()
        self.devs = devs

    def load_config(self):
        """Load AutoMod configuration from a file, or initialize defaults."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                self.config = json.load(file)
        else:
            self.config = {"rules": []}
            self.save_config()

    def save_config(self):
        """Save AutoMod configuration to a file."""
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.config, file, indent=4)

    @app_commands.command(name="setup_automod", description="Set up AutoMod rules from the configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    @is_dev()
    async def setup_automod(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Set up AutoMod rules based on the configuration file.
        """
        try:
            guild = interaction.guild
            if not guild:
                await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
                return

            created_rules = []
            for rule_config in self.config["rules"]:
                name = rule_config["name"]
                regex_patterns = rule_config["regex_patterns"][:10]  # Limit to 10 regex patterns
                allowed_links = rule_config["allowed_links"][:100]  # Limit to 100 allowed words
                blocked_words = rule_config["blocked_words"][:1000]  # Limit to 1000 blocked words

                created_rules=[]
                automod_rule = await guild.create_automod_rule(
                    name=name,
                    event_type=discord.AutoModRuleEventType.message_send,
                    trigger=discord.AutoModTrigger(
                        type=discord.AutoModRuleTriggerType.keyword,
                        regex_patterns=regex_patterns,
                        keyword_filter=blocked_words,
                        allow_list=allowed_links
                    ),
                    actions=[
                        discord.AutoModRuleAction(
                            channel_id=channel.id,
                            type=discord.AutoModRuleActionType.block_message
                        )
                    ],
                    enabled=True,
                    reason=f"AutoMod setup for rule: {name}"
                )

                created_rules.append(automod_rule.name)
                    
            embed = discord.Embed(
                title="AutoMod setup complete!",
                description=f"Created rules:\n- " + "\n- ".join(created_rules),
                color=0x03fcb6
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error in AutoMod setup: {e}")
            await interaction.response.send_message(f"An error occurred. Please contact an administrator.\n```{e}```", ephemeral=True)

    @app_commands.command(name="update_automod", description="Apply changes from the configuration to the server's AutoMod rules.")
    @app_commands.checks.has_permissions(administrator=True)
    @is_dev()
    async def update_automod(self, interaction: discord.Interaction):
        """
        Update AutoMod rules in the server based on the current configuration file.
        """
        try:
            guild = interaction.guild
            if not guild:
                await interaction.response.send_message("This command can only be run in a server.", ephemeral=True)
                return

            # Fetch existing AutoMod rules
            existing_rules = {rule.name: rule for rule in await guild.automod_rules()}

            # Load configuration from a JSON file
            with open("data/AM_conf.json", "r") as config_file:
                config = json.load(config_file)

            # Delete existing rules that are being updated
            for rule_name, rule in existing_rules.items():
                if rule_name in config:
                    await rule.delete(reason="Updating AutoMod rule via bot.")

            # Recreate or update AutoMod rules based on the configuration
            for rule_name, rule_data in config.items():
                actions = [
                    discord.AutoModRuleAction(
                        type=discord.AutoModRuleActionType[rule_data["action_type"]],
                        metadata=discord.AutoModRuleActionMetadata(
                            channel_id=rule_data.get("channel_id"),
                            custom_message=rule_data.get("custom_message")
                        )
                    )
                ]

                trigger = discord.AutoModRuleTriggerType[rule_data["trigger_type"]]

                if trigger == discord.AutoModRuleTriggerType.keyword:
                    trigger_metadata = discord.AutoModRuleTriggerMetadata(
                        keyword_filter=rule_data["keyword_filter"]
                    )
                elif trigger == discord.AutoModRuleTriggerType.spam:
                    trigger_metadata = discord.AutoModRuleTriggerMetadata()
                else:
                    # Handle other trigger types if necessary
                    trigger_metadata = discord.AutoModRuleTriggerMetadata()

                await guild.create_automod_rule(
                    name=rule_name,
                    trigger_type=trigger,
                    trigger_metadata=trigger_metadata,
                    actions=actions,
                    enabled=rule_data.get("enabled", True),
                    exempt_roles=[guild.get_role(role_id) for role_id in rule_data.get("exempt_roles", [])],
                    exempt_channels=[guild.get_channel(channel_id) for channel_id in rule_data.get("exempt_channels", [])],
                    reason="Updating AutoMod rule via bot."
                )

            # Send confirmation message
            embed = discord.Embed(
                title="AutoMod Rules Updated",
                description="The AutoMod rules have been successfully updated from the configuration file.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            # Handle errors
            embed = discord.Embed(
                title="Error Updating AutoMod Rules",
                description=f"An error occurred while updating AutoMod rules:\n```\n{e}\n```",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
