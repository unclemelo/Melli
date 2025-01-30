import discord
from discord import app_commands
from discord.ext import commands
import json
# Load AutoMod preset configurations from file

"""Load AutoMod presets from the given JSON file."""
try:
    with open("data/presets.json", "r") as file:
        Pretesets = json.load(file)
except discord.HTTPException as e:
    # Return an empty dict if file is not found or invalid JSON
    print("JSON didnt load")
# UI for AutoMod settings
class AutoModSettingsView(discord.ui.View):
    """UI view that includes preset selection, role selection, channel selection, and save button for AutoMod settings."""
    def __init__(self, log_channel: discord.TextChannel, guild: discord.Guild):
        super().__init__(timeout=None)
        self.add_item(AutoModPresetSelector())
        self.add_item(AutoModRoleSelector(guild))
        self.add_item(AutoModChannelSelector(guild))
        self.add_item(SaveAutoModConfigButton(log_channel))

# Dropdown menu to select AutoMod presets
class AutoModPresetSelector(discord.ui.Select):
    """Dropdown menu to select the AutoMod security preset."""
    def __init__(self):
        options = [
            discord.SelectOption(label="Low Security", description="Minimal filtering for casual servers"),
            discord.SelectOption(label="Medium Security", description="Balanced filtering for general use"),
            discord.SelectOption(label="High Security", description="Strict filtering for highly moderated servers")
        ]
        super().__init__(
            placeholder="Choose a security level...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        """Handle the preset selection and store it temporarily for later use."""
        if hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        selected_preset = self.values[0]
        interaction.client.temp_data[interaction.user.id] = {"preset": selected_preset}
        # Store the selected preset in temporary data for later use
        interaction.client.temp_data[interaction.user.id]["config"] = Pretesets.get(selected_preset, {})

# Dropdown menu to select exempt roles
class AutoModRoleSelector(discord.ui.Select):
    """Dropdown menu to select exempt roles."""
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        roles = [discord.SelectOption(label=role.name, value=str(role.id)) for role in guild.roles if role.name != "@everyone"]
        super().__init__(
            placeholder="Choose exempt roles...",
            min_values=0,
            max_values=len(roles),
            options=roles
        )

    async def callback(self, interaction: discord.Interaction):
        """Store the selected exempt roles."""
        selected_roles = [self.guild.get_role(int(role_id)) for role_id in self.values]
        interaction.client.temp_data[interaction.user.id]["exempt_roles"] = selected_roles

# Dropdown menu to select exempt channels
class AutoModChannelSelector(discord.ui.Select):
    """Dropdown menu to select exempt channels."""
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        channels = [discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in guild.text_channels]
        super().__init__(
            placeholder="Choose exempt channels...",
            min_values=0,
            max_values=len(channels),
            options=channels
        )

    async def callback(self, interaction: discord.Interaction):
        """Store the selected exempt channels."""
        selected_channels = [self.guild.get_channel(int(channel_id)) for channel_id in self.values]
        interaction.client.temp_data[interaction.user.id]["exempt_channels"] = selected_channels

# Button to save AutoMod settings
class SaveAutoModConfigButton(discord.ui.Button):
    """Button to save and apply the AutoMod settings."""
    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(label="Apply AutoMod Settings", style=discord.ButtonStyle.success)
        self.log_channel = log_channel
        print("AAAAAAAAAAA")

    async def callback(self, interaction: discord.Interaction):
        """Handle the save button callback to apply the AutoMod settings."""
        user_id = interaction.user.id
        bot = interaction.client
        guild = interaction.guild

        await interaction.response.defer(ephemeral=True)

        # Retrieve the selected preset from temporary data
        selected_preset = bot.temp_data.get(user_id, {}).get("preset")
        if not selected_preset:
            # No preset selected, notify the user
            await interaction.followup.send("⚠ No preset selected. Please choose a preset before saving!", ephemeral=True)
            return
        # Load rule data for the selected preset
        rule_data = Pretesets.get(selected_preset, {})
        if not rule_data:
            # Missing or empty preset data
            await interaction.followup.send("⚠ Error: Preset settings not found!", ephemeral=True)
            return
        rule_name = rule_data.get("rule_name", "AutoMod Rule")
        keyword_filter = rule_data.get("keyword_filter", [])
        exempt_roles = bot.temp_data.get(user_id, {}).get("exempt_roles", [])
        exempt_channels = bot.temp_data.get(user_id, {}).get("exempt_channels", [])

        # Attempt to create the AutoMod rule
        try:
            rule = await guild.create_automod_rule(
                name=rule_name,
                event_type=discord.AutoModRuleEventType.message_send,
                trigger_type=discord.AutoModRuleTriggerType.keyword,
                keyword_filter=keyword_filter,
                actions=[
                        discord.AutoModRuleAction(
                            type=discord.AutoModRuleActionType.send_alert_message, 
                            channel=self.log_channel.id
                        )
                    ],
                enabled=True,
                exempt_roles=exempt_roles,
                exempt_channels=exempt_channels,
                reason="Updating AutoMod settings via bot."
            )
            embed = discord.Embed(
                title="✅ AutoMod Settings Applied",
                description=f"AutoMod is now using the **{selected_preset}** security level.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        except discord.HTTPException as e:
            # Handle failure to create the rule
            await interaction.followup.send(f"❌ Failed to create AutoMod rule: {e}", ephemeral=True)


class AutoModManager(commands.Cog):
    """Cog to manage AutoMod setup and settings."""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="automod_setup", description="Configure AutoMod settings for the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_setup(self, interaction: discord.Interaction, log_channel: discord.TextChannel):
        """Command to start the AutoMod setup process."""
        view = AutoModSettingsView(log_channel, interaction.guild)
        embed = discord.Embed(
            title="🔧 AutoMod Configuration",
            description="Select a filtering level, exempt roles, and exempt channels, then apply the settings below.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    """Setup the AutoModManager cog."""
    await bot.add_cog(AutoModManager(bot))
