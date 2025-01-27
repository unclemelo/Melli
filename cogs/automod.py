import discord
import os
from discord import app_commands
from discord.ext import commands
import json

# View for managing AutoMod configuration
class AutoModConfigView(discord.ui.View):
    def __init__(self, alert_channel: discord.TextChannel):
        super().__init__(timeout=None)

        # Pass alert_channel to dropdown
        self.add_item(AutoModPresetDropdown(alert_channel))

        # Button to save configuration
        self.add_item(AutoModSaveButton())

# Dropdown for presets
class AutoModPresetDropdown(discord.ui.Select):
    def __init__(self, alert_channel: discord.TextChannel):
        self.alert_channel = alert_channel

        options = [
            discord.SelectOption(label="Low Guard", description="Minimal filtering, suitable for relaxed environments"),
            discord.SelectOption(label="Moderate Guard", description="Balanced filtering for general use"),
            discord.SelectOption(label="High Guard", description="Strict filtering for high-security needs")
        ]
        super().__init__(
            placeholder="Select a preset...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        # Store selected preset in temp_data
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        preset = self.values[0]
        interaction.client.temp_data[interaction.user.id] = {"preset": preset}

        # Define preset details and their configurations
        preset_details = {
            "Low Guard": "**Low Guard Preset**\n- Minimal keyword filtering\n- No regex patterns\n- Allows most content",
            "Moderate Guard": "**Moderate Guard Preset**\n- Balanced keyword filtering\n- Basic regex patterns applied\n- Suitable for most communities",
            "High Guard": "**High Guard Preset**\n- Extensive keyword filtering\n- Advanced regex patterns\n- Strict rules for secure environments"
        }

        # Example configurations for each preset
        preset_configurations = {
            "Low Guard": {
                "action_type": "send_alert_message",
                "channel_id": self.alert_channel.id,
                "custom_message": "Please adhere to the rules!",
                "regex_patterns": [],
                "keyword_filter": [],
                "enabled": True,
                "exempt_roles": [],
                "exempt_channels": []
            },
            "Moderate Guard": {
                "action_type": "send_alert_message",
                "channel_id": self.alert_channel.id,
                "custom_message": "This message violates community guidelines.",
                "regex_patterns": ["badword1", "badword2"],
                "keyword_filter": ["spam", "offensive"],
                "enabled": True,
                "exempt_roles": [],
                "exempt_channels": []
            },
            "High Guard": {
                "action_type": "send_alert_message",
                "channel_id": self.alert_channel.id,
                "custom_message": "Your message has been blocked due to policy violations.",
                "regex_patterns": [".*badword.*", "offensive[0-9]*"],
                "keyword_filter": ["spam", "offensive", "profanity"],
                "enabled": True,
                "exempt_roles": [],
                "exempt_channels": []
            }
        }

        # Inject configuration into temp_data
        interaction.client.temp_data[interaction.user.id]["config"] = preset_configurations.get(preset, {})

        embed = discord.Embed(
            title="Preset Selected",
            description=preset_details.get(preset, "Unknown preset"),
            color=discord.Color.yellow()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

# Button to save configuration
class AutoModSaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Save Configuration", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        user_data = interaction.client.temp_data.get(interaction.user.id, {}).get("config", {})

        # Save configuration to file
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
    async def automod_config(self, interaction: discord.Interaction, alert_channel: discord.TextChannel):
        view = AutoModConfigView(alert_channel)
        embed = discord.Embed(
            title="AutoMod Configuration",
            description="Select a preset or customize your settings using the dropdown menu below.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoModManagement(bot))
