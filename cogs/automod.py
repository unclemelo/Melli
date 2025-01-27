import discord
import os
from discord import app_commands
from discord.ext import commands
import json

# View for managing AutoMod configuration
class AutoModConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Edit Config", style=discord.ButtonStyle.primary)
    async def edit_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Trigger the first modal
            await interaction.response.send_modal(AutoModGeneralSettingsModal())
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# General Settings Modal
class AutoModGeneralSettingsModal(discord.ui.Modal, title="General Settings"):
    action_type = discord.ui.Select(
        placeholder="Select an action type",
        options=[
            discord.SelectOption(label="Send Alert Message", value="send_alert_message"),
            discord.SelectOption(label="Delete Message", value="delete_message"),
            discord.SelectOption(label="Timeout User", value="timeout_user")
        ]
    )
    alert_channel = discord.ui.ChannelSelect(
        placeholder="Select an alert channel",
        channel_types=[discord.ChannelType.text]
    )

    def __init__(self):
        super().__init__()
        self.add_item(self.action_type)
        self.add_item(self.alert_channel)

    async def on_submit(self, interaction: discord.Interaction):
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        interaction.client.temp_data[interaction.user.id] = {
            "action_type": self.action_type.values[0],
            "alert_channel": self.alert_channel.values[0] if self.alert_channel.values else None
        }

        await interaction.response.send_modal(AutoModFiltersModal())

# Filters Modal
class AutoModFiltersModal(discord.ui.Modal, title="Filters"):
    regex_patterns = discord.ui.Select(
        placeholder="Select Regex Patterns",
        options=[
            discord.SelectOption(label="Pattern 1", value="pattern1"),
            discord.SelectOption(label="Pattern 2", value="pattern2"),
            discord.SelectOption(label="Pattern 3", value="pattern3")
        ],
        min_values=1,
        max_values=3
    )
    keyword_filter = discord.ui.TextInput(
        label="Custom Keyword Filter (comma-separated)",
        placeholder="e.g., customword1,customword2",
        required=False
    )

    def __init__(self):
        super().__init__()
        self.add_item(self.regex_patterns)
        self.add_item(self.keyword_filter)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = interaction.client.temp_data.get(interaction.user.id, {})
        user_data.update({
            "regex_patterns": self.regex_patterns.values,
            "keyword_filter": self.keyword_filter.value.split(",") if self.keyword_filter.value else []
        })

        interaction.client.temp_data[interaction.user.id] = user_data
        await interaction.response.send_modal(AutoModExemptionsModal())

# Exemptions Modal
class AutoModExemptionsModal(discord.ui.Modal, title="Exemptions"):
    exempt_roles = discord.ui.RoleSelect(
        placeholder="Select roles to exempt",
        min_values=0,
        max_values=5
    )
    exempt_channels = discord.ui.ChannelSelect(
        placeholder="Select channels to exempt",
        channel_types=[discord.ChannelType.text],
        min_values=0,
        max_values=5
    )

    def __init__(self):
        super().__init__()
        self.add_item(self.exempt_roles)
        self.add_item(self.exempt_channels)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = interaction.client.temp_data.get(interaction.user.id, {})
        user_data.update({
            "exempt_roles": [role.id for role in self.exempt_roles.values],
            "exempt_channels": [channel.id for channel in self.exempt_channels.values]
        })

        directory = "data/Automod_Configs"
        os.makedirs(directory, exist_ok=True)
        file_name = f"{directory}/{interaction.guild.id}.json"

        with open(file_name, "w") as config_file:
            json.dump(user_data, config_file, indent=4)

        embed = discord.Embed(
            title="Configuration Saved",
            description="The AutoMod configuration has been successfully saved.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Main Cog
class AutoModManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="automod_config", description="Open the AutoMod configuration interface.")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_config(self, interaction: discord.Interaction):
        view = AutoModConfigView()
        await interaction.response.send_message(
            "Use the button below to edit AutoMod configuration.",
            view=view,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(AutoModManagement(bot))
