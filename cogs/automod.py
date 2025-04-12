import discord
from discord import app_commands
from discord.ext import commands
import json

# Load AutoMod preset configurations from file
try:
    with open("data/presets.json", "r") as file:
        Presets = json.load(file)
except discord.HTTPException:
    print("JSON didn't load")


class AutoModSettingsView(discord.ui.View):
    """UI view that includes preset selection, role selection, channel selection, and save button for AutoMod settings."""

    def __init__(self, log_channel: discord.TextChannel, guild: discord.Guild):
        super().__init__(timeout=None)
        self.add_item(AutoModPresetSelector())
        self.add_item(AutoModRoleSelector(guild))
        self.add_item(AutoModChannelSelector(guild))
        self.add_item(SaveAutoModConfigButton(log_channel))


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
        user_id = interaction.user.id

        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        selected_preset = self.values[0]
        interaction.client.temp_data[user_id]["preset"] = selected_preset
        interaction.client.temp_data[user_id]["config"] = Presets.get(selected_preset, {})

        await interaction.response.send_message(f"✅ Preset **{selected_preset}** selected!", ephemeral=True)


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
        user_id = interaction.user.id

        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        selected_roles = [self.guild.get_role(int(role_id)) for role_id in self.values]
        interaction.client.temp_data[user_id]["exempt_roles"] = selected_roles

        await interaction.response.send_message("✅ Exempt roles updated!", ephemeral=True)


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
        user_id = interaction.user.id

        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        selected_channels = [self.guild.get_channel(int(channel_id)) for channel_id in self.values]
        interaction.client.temp_data[user_id]["exempt_channels"] = selected_channels

        await interaction.response.send_message("✅ Exempt channels updated!", ephemeral=True)


class SaveAutoModConfigButton(discord.ui.Button):
    """Button to save and apply the AutoMod settings."""

    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(label="Apply AutoMod Settings", style=discord.ButtonStyle.success)
        self.log_channel = log_channel
        print("Melo, you baka")

    async def callback(self, interaction: discord.Interaction):
        """Handle the save button callback to apply the AutoMod settings."""
        user_id = interaction.user.id
        bot = interaction.client
        guild = interaction.guild

        await interaction.response.defer(ephemeral=True)
        user_temp_data = bot.temp_data.get(user_id, {})

        if not user_temp_data:
            await interaction.followup.send("⚠ No AutoMod settings found. Please select a preset and try again!", ephemeral=True)
            return

        selected_preset = user_temp_data.get("preset")
        if not selected_preset:
            await interaction.followup.send("⚠ No preset selected. Please choose a preset before saving!", ephemeral=True)
            return

        rule_data = Presets.get(selected_preset, {})
        if not rule_data:
            await interaction.followup.send("⚠ Error: Preset settings not found!", ephemeral=True)
            return

        rule_name = rule_data.get("rule_name", "AutoMod Rule")
        keyword_filter = rule_data.get("keyword_filter", [])
        RegExs_list = rule_data.get("regex_patterns", [])
        AllowList = rule_data.get("allowed_keywords", [])

        exempt_roles = [
            guild.get_role(int(role.id)) for role in user_temp_data.get("exempt_roles", [])
            if guild.get_role(int(role.id)) is not None
        ]

        exempt_channels = [
            guild.get_channel(int(channel.id)) for channel in user_temp_data.get("exempt_channels", [])
            if guild.get_channel(int(channel.id)) is not None
        ]

        if not self.log_channel:
            await interaction.followup.send("⚠ Log channel not found. Please try again!", ephemeral=True)
            return

        try:
            rule = await guild.create_automod_rule(
                name=rule_name,
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(
                    type=discord.AutoModRuleTriggerType.keyword,
                    keyword_filter=keyword_filter,
                    allow_list=AllowList,
                    regex_patterns=RegExs_list,
                ),
                actions=[
                    discord.AutoModRuleAction(
                        type=discord.AutoModRuleActionType.send_alert_message,
                        channel_id=self.log_channel.id
                    ),
                    discord.AutoModRuleAction(
                        type=discord.AutoModRuleActionType.block_message
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
            embed.set_footer(text="Our presets are always improving, stay updated on your preset by joining the support server. [here](https://discord.gg/PD2fpwGyx6)")

            await interaction.followup.send(embed=embed)

        except discord.HTTPException as e:
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
