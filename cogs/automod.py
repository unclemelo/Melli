import discord
import os
from discord import app_commands
from discord.ext import commands
import json

# Load AutoMod preset configurations from file
PRESETS_FILE = "data/Automod_Configs/presets.json"
DEBUG_CHANNEL_ID = 1308048388637462558 

def load_presets():
    try:
        with open(PRESETS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

preset_configurations = load_presets()

async def send_debug_log(bot, message):
    """Helper function to send debug logs to a specific channel."""
    channel = bot.get_channel(DEBUG_CHANNEL_ID)
    if channel:
        await channel.send(f"🛠️ **Debug Log:** {message}")

# UI for AutoMod settings
class AutoModSettingsView(discord.ui.View):
    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.add_item(AutoModPresetSelector(log_channel))
        self.add_item(SaveAutoModConfigButton())

# Dropdown menu to select AutoMod presets
class AutoModPresetSelector(discord.ui.Select):
    def __init__(self, log_channel: discord.TextChannel):
        self.log_channel = log_channel

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
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        selected_preset = self.values[0]
        interaction.client.temp_data[interaction.user.id] = {"preset": selected_preset}

        # Debug log
        await send_debug_log(interaction.client, f"{interaction.user} selected `{selected_preset}` preset.")

        # Detailed descriptions of each preset
        preset_explanations = {
            "Low Security": "**Low Security Mode**\n- Allows most messages\n- Minimal keyword filtering\n- Best for casual servers",
            "Medium Security": "**Medium Security Mode**\n- Blocks common offensive words\n- Uses basic pattern recognition\n- Suitable for most communities",
            "High Security": "**High Security Mode**\n- Strict message filtering\n- Advanced pattern detection\n- Best for high-moderation servers"
        }

        interaction.client.temp_data[interaction.user.id]["config"] = preset_configurations.get(selected_preset, {})

        embed = discord.Embed(
            title="AutoMod Preset Selected",
            description=preset_explanations.get(selected_preset, "Unknown preset"),
            color=discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

# Button to save AutoMod settings
class SaveAutoModConfigButton(discord.ui.Button):
    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(label="Apply AutoMod Settings", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        bot = interaction.client
        
        # ✅ Defer the response to prevent interaction timeout
        await interaction.response.defer(ephemeral=True)
        await send_debug_log(bot, f"⏳ Processing AutoMod settings for {interaction.user}...")

        selected_preset = bot.temp_data.get(user_id, {}).get("preset")
        if not selected_preset:
            await send_debug_log(bot, "⚠ No preset selected - skipping AutoMod rule creation.")
            await interaction.followup.send("⚠ No preset selected. Please choose a preset before saving!", ephemeral=True)
            return
        
        guild = interaction.guild
        rule_data = preset_configurations.get(selected_preset, {})

        if not rule_data:
            await send_debug_log(bot, f"⚠ Preset `{selected_preset}` is empty or missing in `presets.json`.")
            await interaction.followup.send("⚠ Error: Preset settings not found!", ephemeral=True)
            return

        await send_debug_log(bot, f"📜 Loaded rule data for `{selected_preset}`: {rule_data}")

        rule_name = rule_data.get("rule_name", "AutoMod Rule")
        regex_patterns = rule_data.get("regex_patterns", [])
        keyword_filter = rule_data.get("keyword_filter", [])
        exempt_roles = [guild.get_role(role_id) for role_id in rule_data.get("exempt_roles", []) if guild.get_role(role_id)]
        exempt_channels = [guild.get_channel(channel_id) for channel_id in rule_data.get("exempt_channels", []) if guild.get_channel(channel_id)]

        await send_debug_log(bot, f"✅ Exempt Roles: {exempt_roles}")
        await send_debug_log(bot, f"✅ Exempt Channels: {exempt_channels}")

        # ✅ Save settings and check for errors
        try:
            with open(PRESETS_FILE, "w") as config_file:
                json.dump(preset_configurations, config_file, indent=4)
            await send_debug_log(bot, "💾 Preset configuration saved successfully.")
        except Exception as e:
            await send_debug_log(bot, f"❌ Failed to save presets: {e}")

        embed = discord.Embed(
            title="✅ AutoMod Settings Applied",
            description=f"AutoMod is now using the **{selected_preset}** security level.",
            color=discord.Color.green()
        )

        await send_debug_log(bot, f"⚙️ Preparing to create AutoMod rule `{rule_name}`.")

        # ✅ AutoMod Rule Setup
        try:
            actions = [
                discord.AutoModRuleAction(
                    channel_id=self.log_channel.id,
                    type=discord.AutoModRuleActionType.send_alert_message
                )
            ]
        except Exception as e:
            await send_debug_log(bot, f"❌ Failed to create Automod actions: {e}")


        try:
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
                exempt_roles=exempt_roles,
                exempt_channels=exempt_channels,
                reason="Updating AutoMod settings via bot."
            )
            await send_debug_log(bot, f"✅ Successfully created AutoMod rule `{rule_name}`.")
            await interaction.followup.send(embed=embed)  # ✅ Send success message after processing
        except discord.HTTPException as e:
            await send_debug_log(bot, f"❌ Failed to create AutoMod rule: {e}")
            await interaction.followup.send(f"❌ Failed to create AutoMod rule: {e}", ephemeral=True)

# AutoMod Command Cog
class AutoModManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="automod_setup", description="Configure AutoMod settings for the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_setup(self, interaction: discord.Interaction, log_channel: discord.TextChannel):
        """Allows admins to set up AutoMod filtering for the server."""
        view = AutoModSettingsView(log_channel)
        embed = discord.Embed(
            title="🔧 AutoMod Configuration",
            description="Select a filtering level and apply the settings below.",
            color=discord.Color.blue()
        )

        await send_debug_log(self.bot, f"{interaction.user} initiated AutoMod setup.")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoModManager(bot))
    await send_debug_log(bot, "📢 AutoModManager cog loaded.")
