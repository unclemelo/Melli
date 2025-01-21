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

                ##Test
                try:
                    automod_rule = await guild.create_automod_rule(
                        name=name,
                        event_type=discord.AutoModRuleEventType.message_send,
                        trigger=discord.AutoModTrigger(
                            type=discord.AutoModRuleTriggerType.keyword,
                            regex_patterns=["regex1"]
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

                    #created_rules.append(automod_rule.name)
                except Exception as e:
                    await interaction.response.send_message(f"An error occurred.TEST FAILED.\n```{e}```\n```{name}```", ephemeral=True)
                    

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
                await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
                return

            existing_rules = {rule.name: rule for rule in await guild.automod_rules()}

            updated_rules = []
            for rule_config in self.config["rules"]:
                name = rule_config["name"]
                regex_patterns = rule_config["regex_patterns"][:10]  # Limit to 10 regex patterns
                allowed_links = rule_config["allowed_links"][:100]  # Limit to 100 allowed words
                blocked_words = rule_config["blocked_words"][:1000]  # Limit to 1000 blocked words

                if name in existing_rules:
                    # Update the existing rule
                    rule = existing_rules[name]
                    await rule.edit(
                        trigger=discord.AutoModTrigger(
                            type=discord.AutoModRuleTriggerType.keyword,
                            regex_patterns=regex_patterns,
                            keyword_filter=blocked_words,
                            allow_list=allowed_links
                        ),
                        enabled=True,
                        reason=f"Updated rule: {name}"
                    )
                    updated_rules.append(name)
                else:
                    # Create a new rule if it doesn't exist
                    await guild.create_automod_rule(
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
                                type=discord.AutoModRuleActionType.block_message
                            )
                        ],
                        enabled=True,
                        reason=f"Created new rule: {name}"
                    )
                    updated_rules.append(name)

            embed = discord.Embed(
                title="AutoMod updated!",
                description=f"Updated or created rules:\n- " + "\n- ".join(updated_rules),
                color=0x03fcb6
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error in AutoMod update: {e}")
            await interaction.response.send_message("An error occurred while updating AutoMod rules.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
