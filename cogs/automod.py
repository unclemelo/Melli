import discord
import os
from discord import app_commands
from discord.ext import commands
import json

class AutoModConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Upload Config", style=discord.ButtonStyle.primary)
    async def upload_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(AutoModConfigModal())
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)


class AutoModConfigModal(discord.ui.Modal, title="Upload AutoMod Configuration"):
    action_type = discord.ui.TextInput(
        label="Action Type",
        placeholder="e.g., send_alert_message",
        required=False
    )
    channel_id = discord.ui.TextInput(
        label="Channel ID",
        placeholder="Enter the target channel ID",
        required=False
    )
    custom_message = discord.ui.TextInput(
        label="Custom Message",
        placeholder="e.g., Please adhere to the rules!",
        required=False
    )
    regex_patterns = discord.ui.TextInput(
        label="Regex Patterns (comma-separated)",
        placeholder="e.g., badword1,badword2",
        required=False
    )
    keyword_filter = discord.ui.TextInput(
        label="Keyword Filter (comma-separated)",
        placeholder="e.g., badword1,badword2",
        required=False
    )
    exempt_roles = discord.ui.TextInput(
        label="Exempt Roles (comma-separated)",
        placeholder="e.g., 123456789012345678,987654321098765432",
        required=False
    )
    exempt_channels = discord.ui.TextInput(
        label="Exempt Channels (comma-separated)",
        placeholder="e.g., 123456789012345678,987654321098765432",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.guild:
            embed = discord.Embed(
                title="Error",
                description="This command must be used in a server.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Construct the configuration from input fields
            config = {
                "action_type": self.action_type.value or "send_alert_message",
                "channel_id": int(self.channel_id.value) if self.channel_id.value else 0,
                "custom_message": self.custom_message.value or "Please adhere to the rules!",
                "regex_patterns": [x.strip() for x in self.regex_patterns.value.split(",")] if self.regex_patterns.value else [],
                "keyword_filter": [x.strip() for x in self.keyword_filter.value.split(",")] if self.keyword_filter.value else [],
                "exempt_roles": [x.strip() for x in self.exempt_roles.value.split(",")] if self.exempt_roles.value else [],
                "exempt_channels": [x.strip() for x in self.exempt_channels.value.split(",")] if self.exempt_channels.value else [],
            }

            # Save configuration to a file
            directory = "data/Automod_Configs"
            os.makedirs(directory, exist_ok=True)
            file_name = os.path.join(directory, f"{interaction.guild.id}.json")

            with open(file_name, "w") as config_file:
                json.dump({"rule1": config}, config_file, indent=4)

            embed = discord.Embed(
                title="Configuration Uploaded",
                description="The new AutoMod configuration has been successfully uploaded.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)



class AutoModManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="build_automod", description="Apply changes from the configuration to the server's AutoMod rules.")
    @app_commands.checks.has_permissions(administrator=True)
    async def update_automod(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            guild = interaction.guild
            if not guild:
                await interaction.response.send_message("This command can only be run in a server.", ephemeral=True)
                return

            # Fetch existing AutoMod rules
            existing_rules = {rule.name: rule for rule in await guild.fetch_automod_rules()}

            # Load configuration from JSON file
            with open("data/AM_conf.json", "r") as config_file:
                config = json.load(config_file)

            # Delete existing rules
            for rule_name, rule in existing_rules.items():
                if rule_name in config:
                    await rule.delete(reason="Updating AutoMod rule via bot.")

            # Update AutoMod rules
            for rule_name, rule_data in config.items():
                regex_patterns = rule_data.get("regex_patterns", [])[:10]
                keyword_filter = rule_data.get("keyword_filter", [])[:1000]

                actions = [
                    discord.AutoModRuleAction(
                        type=discord.AutoModRuleActionType[rule_data["action_type"]],
                        channel_id=channel.id
                    )
                ]

                await guild.create_automod_rule(
                    name=rule_name,
                    event_type=discord.AutoModRuleEventType.message_send,
                    trigger=discord.AutoModTrigger(
                        type=discord.AutoModRuleTriggerType.keyword,
                        regex_patterns=regex_patterns,
                        keyword_filter=keyword_filter,
                    ),
                    actions=actions,
                    enabled=rule_data.get("enabled", True),
                    exempt_roles=[guild.get_role(role_id) for role_id in rule_data.get("exempt_roles", [])],
                    exempt_channels=[guild.get_channel(channel_id) for channel_id in rule_data.get("exempt_channels", [])],
                    reason="Updating AutoMod rule via bot."
                )

            # Confirmation message
            embed = discord.Embed(
                title="AutoMod Rules Updated",
                description="The AutoMod rules have been successfully updated.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error Updating AutoMod Rules",
                description=f"An error occurred while updating AutoMod rules:\n```\n{e}\n```",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="automod_config", description="Open the AutoMod configuration interface.")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_config(self, interaction: discord.Interaction):
        view = AutoModConfigView()
        await interaction.response.send_message("Use the buttons below to manage AutoMod configuration.", view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AutoModManagement(bot))
