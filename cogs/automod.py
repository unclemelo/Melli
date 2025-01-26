import discord
import os
from discord import app_commands
from discord.ext import commands
import json

class AutoModConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Edit Config", style=discord.ButtonStyle.primary)
    async def edit_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(AutoModPage1())
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)


class AutoModPage1(discord.ui.Modal, title="Page 1: General Settings"):
    def __init__(self):
        super().__init__()
        self.add_item(ActionTypeSelect())

    channel_id = discord.ui.TextInput(
        label="Channel ID",
        placeholder="Enter the target channel ID",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Ensure temp_data exists
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        # Save the action type selected
        action_type = interaction.client.temp_data.get(interaction.user.id, {}).get("action_type", "send_alert_message")

        # Save the data
        interaction.client.temp_data[interaction.user.id] = {
            "action_type": action_type,
            "channel_id": self.channel_id.value,
        }

        # Trigger the second modal
        await interaction.response.send_modal(AutoModPage2())


class ActionTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Send Alert Message", value="send_alert_message", description="Send a warning message"),
            discord.SelectOption(label="Block Message", value="block_message", description="Prevent the message from being sent"),
            discord.SelectOption(label="Timeout User", value="timeout_user", description="Temporarily mute the user"),
        ]
        super().__init__(placeholder="Select an action type...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Store the user's selection temporarily
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}
        interaction.client.temp_data[interaction.user.id] = {"action_type": self.values[0]}
        await interaction.response.send_message(f"You selected: {self.values[0]}", ephemeral=True)


class AutoModPage2(discord.ui.Modal, title="Page 2: Filters"):
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

    async def on_submit(self, interaction: discord.Interaction):
        user_data = interaction.client.temp_data.get(interaction.user.id, {})
        user_data.update({
            "regex_patterns": self.regex_patterns.value.split(",") if self.regex_patterns.value else [],
            "keyword_filter": self.keyword_filter.value.split(",") if self.keyword_filter.value else [],
        })

        interaction.client.temp_data[interaction.user.id] = user_data
        await interaction.response.send_modal(AutoModPage3())


class AutoModPage3(discord.ui.Modal, title="Page 3: Exemptions"):
    exempt_roles = discord.ui.TextInput(
        label="Exempt Roles (comma-separated)",
        placeholder="e.g., Role1,Role2",
        required=False
    )
    exempt_channels = discord.ui.TextInput(
        label="Exempt Channels (comma-separated)",
        placeholder="e.g., Channel1,Channel2",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_data = interaction.client.temp_data.get(interaction.user.id, {})
        user_data.update({
            "exempt_roles": self.exempt_roles.value.split(",") if self.exempt_roles.value else [],
            "exempt_channels": self.exempt_channels.value.split(",") if self.exempt_channels.value else [],
        })

        directory = "data/Automod_Configs"
        os.makedirs(directory, exist_ok=True)
        file_name = f"{directory}/{interaction.guild.id}.json"

        with open(file_name, "w") as config_file:
            json.dump(user_data, config_file, indent=4)

        embed = discord.Embed(
            title="Configuration Uploaded",
            description="The AutoMod configuration has been successfully uploaded.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


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
