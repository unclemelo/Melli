import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import hashlib
import re
from util.command_checks import command_enabled

# ---- util funcs moved to util/automod.py (import them) ----
from util.automod import (
    hash_preset, get_temp_data, load_json, save_json, apply_automod_rule
)

# Load presets once here
Presets = load_json("data/presets.json")

# Regex to extract IDs from mentions (roles/channels)
ID_EXTRACTOR = re.compile(r"<@&?(\d+)>|(\d+)")

# --- Modal classes for manual input when >25 roles/channels ---

class ManualRoleInputModal(discord.ui.Modal, title="Enter exempt roles manually"):
    input_roles = discord.ui.TextInput(
        label="Roles (mention or ID separated by spaces or commas)",
        style=discord.TextStyle.paragraph,
        placeholder="@Moderator, 123456789012345678",
        required=True,
        max_length=400
    )

    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.guild = guild

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.input_roles.value
        role_ids = set()
        for part in re.split(r"[,\s]+", raw):
            if not part.strip():
                continue
            match = ID_EXTRACTOR.match(part)
            if match:
                role_id = int(match.group(1) or match.group(2))
                if self.guild.get_role(role_id):
                    role_ids.add(role_id)
        roles = [self.guild.get_role(rid) for rid in role_ids if self.guild.get_role(rid)]
        data = get_temp_data(interaction.client, interaction.user.id)
        data["exempt_roles"] = roles
        await interaction.response.send_message(
            f"✅ Exempt roles manually updated ({len(roles)} roles).",
            ephemeral=True
        )


class ManualChannelInputModal(discord.ui.Modal, title="Enter exempt channels manually"):
    input_channels = discord.ui.TextInput(
        label="Channels (mention or ID separated by spaces or commas)",
        style=discord.TextStyle.paragraph,
        placeholder="#general, 123456789012345678",
        required=True,
        max_length=400
    )

    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.guild = guild

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.input_channels.value
        channel_ids = set()
        for part in re.split(r"[,\s]+", raw):
            if not part.strip():
                continue
            match = ID_EXTRACTOR.match(part)
            if match:
                channel_id = int(match.group(1) or match.group(2))
                if self.guild.get_channel(channel_id):
                    channel_ids.add(channel_id)
        channels = [self.guild.get_channel(cid) for cid in channel_ids if self.guild.get_channel(cid)]
        data = get_temp_data(interaction.client, interaction.user.id)
        data["exempt_channels"] = channels
        await interaction.response.send_message(
            f"✅ Exempt channels manually updated ({len(channels)} channels).",
            ephemeral=True
        )

# --- UI Selectors ---

class AutoModPresetSelector(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=data.get("description", "No description"))
            for name, data in Presets.items()
        ]
        super().__init__(placeholder="Choose a security level...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        data = get_temp_data(interaction.client, interaction.user.id)
        selected_preset = self.values[0]
        data["preset"] = selected_preset
        data["config"] = Presets.get(selected_preset, {})
        await interaction.response.send_message(f"✅ Preset **{selected_preset}** selected!", ephemeral=True)


class AutoModRoleSelector(discord.ui.Select):
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        roles = [discord.SelectOption(label=role.name, value=str(role.id)) for role in guild.roles if role.name != "@everyone"]
        super().__init__(placeholder="Choose exempt roles...", min_values=0, max_values=len(roles), options=roles)

    async def callback(self, interaction: discord.Interaction):
        data = get_temp_data(interaction.client, interaction.user.id)
        data["exempt_roles"] = [self.guild.get_role(int(role_id)) for role_id in self.values]
        await interaction.response.send_message("✅ Exempt roles updated!", ephemeral=True)


class AutoModChannelSelector(discord.ui.Select):
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        channels = [discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in guild.text_channels]
        super().__init__(placeholder="Choose exempt channels...", min_values=0, max_values=len(channels), options=channels)

    async def callback(self, interaction: discord.Interaction):
        data = get_temp_data(interaction.client, interaction.user.id)
        data["exempt_channels"] = [self.guild.get_channel(int(channel_id)) for channel_id in self.values]
        await interaction.response.send_message("✅ Exempt channels updated!", ephemeral=True)

# --- Buttons ---

class ManualInputFallbackButton(discord.ui.Button):
    def __init__(self, config_type: str, guild: discord.Guild):
        super().__init__(label=f"Enter {config_type} manually", style=discord.ButtonStyle.secondary, custom_id=config_type)
        self.config_type = config_type
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        # Open modal for manual input
        if self.config_type == "roles":
            modal = ManualRoleInputModal(self.guild)
        elif self.config_type == "channels":
            modal = ManualChannelInputModal(self.guild)
        else:
            await interaction.response.send_message("Invalid config type for manual input.", ephemeral=True)
            return
        await interaction.response.send_modal(modal)


class SaveAutoModConfigButton(discord.ui.Button):
    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(label="Apply AutoMod Settings", style=discord.ButtonStyle.success)
        self.log_channel = log_channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = get_temp_data(interaction.client, interaction.user.id)

        try:
            rule_data = data.get("config", {})
            exempt_roles = data.get("exempt_roles", [])
            exempt_channels = data.get("exempt_channels", [])

            await apply_automod_rule(interaction.guild, self.log_channel, rule_data, exempt_roles, exempt_channels)

            embed = discord.Embed(
                title="✅ AutoMod Settings Applied",
                description=f"AutoMod is now using the **{data.get('preset')}** preset.",
                color=discord.Color.magenta()
            )

            regex_patterns = rule_data.get("regex_patterns", [])
            keyword_filters = rule_data.get("keyword_filter", [])
            allowed_keywords = rule_data.get("allowed_keywords", [])

            embed.add_field(
                name="🧠 Regular Expressions",
                value=f"```regex\n{chr(10).join(regex_patterns) if regex_patterns else 'None'}```",
                inline=False
            )

            embed.add_field(
                name="📝 Blocked Keywords",
                value=", ".join(keyword_filters) if keyword_filters else "None",
                inline=False
            )

            embed.add_field(
                name="🚫 Allowed Keywords",
                value=", ".join(allowed_keywords) if allowed_keywords else "None",
                inline=False
            )

            embed.add_field(
                name="🎭 Exempt Roles",
                value=", ".join(role.mention for role in exempt_roles if role) if exempt_roles else "None",
                inline=True
            )

            embed.add_field(
                name="💬 Exempt Channels",
                value=", ".join(channel.mention for channel in exempt_channels if channel) if exempt_channels else "None",
                inline=True
            )

            embed.set_footer(text=f"📢 Alerts will be sent to: #{self.log_channel.name}")

            await interaction.followup.send(embed=embed)

            # Save applied preset and hash
            applied = load_json("data/applied_presets.json")
            applied[str(interaction.guild.id)] = {"preset": data.get("preset"), "hash": hash_preset(rule_data)}
            save_json("data/applied_presets.json", applied)

        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed to create AutoMod rule: {e}", ephemeral=True)


# --- Main View with improved role/channel handling ---
class AutoModSettingsView(discord.ui.View):
    def __init__(self, log_channel: discord.TextChannel, guild: discord.Guild):
        super().__init__(timeout=None)
        self.guild = guild
        self.log_channel = log_channel
        self.add_item(AutoModPresetSelector())

        # Roles
        if len(guild.roles) <= 25:
            self.add_item(AutoModRoleSelector(guild))
        else:
            self.add_item(ManualInputFallbackButton("roles", guild))

        # Channels
        if len(guild.text_channels) <= 25:
            self.add_item(AutoModChannelSelector(guild))
        else:
            self.add_item(ManualInputFallbackButton("channels", guild))

        self.add_item(SaveAutoModConfigButton(log_channel))


# --- Cog class ---

class AutoModManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_presets_task.start()

    @tasks.loop(hours=5)
    async def update_presets_task(self):
        await self.bot.wait_until_ready()
        try:
            applied = load_json("data/applied_presets.json")
            current = load_json("data/presets.json")
        except Exception as e:
            print(f"Error reading preset files: {e}")
            return

        for guild in self.bot.guilds:
            data = applied.get(str(guild.id))
            if not data:
                continue
            preset_name = data.get("preset")
            current_data = current.get(preset_name)
            if not current_data:
                continue

            new_hash = hash_preset(current_data)
            if new_hash != data.get("hash"):
                try:
                    await guild.owner.send(
                        f"🔄 AutoMod preset '{preset_name}' has changed and was auto-updated on {guild.name}."
                    )
                    applied[str(guild.id)]["hash"] = new_hash
                except Exception as e:
                    print(f"Failed to DM owner of {guild.name}: {e}")

        save_json("data/applied_presets.json", applied)

    # Setup command with modal-enabled UI
    @app_commands.command(name="setup", description="Interactively set up AutoMod for your server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @command_enabled()
    async def setup_automod(self, interaction: discord.Interaction):
        log_channel = discord.utils.get(interaction.guild.text_channels, name="mod-logs") or interaction.channel
        view = AutoModSettingsView(log_channel, interaction.guild)
        await interaction.response.send_message(
            "🔧 Use the menu below to configure AutoMod settings.", view=view, ephemeral=True
        )

    # Force update preset command
    @app_commands.command(name="force_update", description="Manually update the AutoMod preset.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @command_enabled()
    async def force_update(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            applied = load_json("data/applied_presets.json")
            current = load_json("data/presets.json")

            settings = applied.get(str(guild.id))
            if not settings:
                await interaction.response.send_message("❌ No preset applied yet.", ephemeral=True)
                return

            preset_name = settings["preset"]
            rule_data = current.get(preset_name)
            await apply_automod_rule(guild, interaction.channel, rule_data, [], [])

            settings["hash"] = hash_preset(rule_data)
            save_json("data/applied_presets.json", applied)
            await interaction.response.send_message(f"✅ AutoMod preset **{preset_name}** manually updated!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    # New command: show current AutoMod config summary
    @app_commands.command(name="show_config", description="Show current AutoMod configuration for this server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @command_enabled()
    async def show_config(self, interaction: discord.Interaction):
        applied = load_json("data/applied_presets.json")
        current = load_json("data/presets.json")
        data = applied.get(str(interaction.guild.id))

        if not data:
            await interaction.response.send_message("❌ No AutoMod configuration found for this server.", ephemeral=True)
            return

        preset_name = data.get("preset")
        rule_data = current.get(preset_name, {})

        exempt_roles = []
        exempt_channels = []
        # Try to read temp data for current user for convenience
        temp = get_temp_data(self.bot, interaction.user.id)
        if "exempt_roles" in temp:
            exempt_roles = temp["exempt_roles"]
        if "exempt_channels" in temp:
            exempt_channels = temp["exempt_channels"]

        embed = discord.Embed(
            title=f"AutoMod Configuration: {preset_name}",
            color=discord.Color.blue()
        )

        regex_patterns = rule_data.get("regex_patterns", [])
        keyword_filters = rule_data.get("keyword_filter", [])
        allowed_keywords = rule_data.get("allowed_keywords", [])

        embed.add_field(
            name="🧠 Regular Expressions",
            value=f"```regex\n{chr(10).join(regex_patterns) if regex_patterns else 'None'}```",
            inline=False
        )

        blocked = ', '.join(keyword_filters) if keyword_filters else 'None'
        allowed = ', '.join(allowed_keywords) if allowed_keywords else 'None'

        embed.add_field(
            name="📝 Blocked Keywords",
            value=f"```\n{blocked}\n```",
            inline=False
        )

        embed.add_field(
            name="🚫 Allowed Keywords",
            value=f"```\n{allowed}\n```",
            inline=False
        )


        embed.add_field(
            name="🎭 Exempt Roles",
            value=", ".join(role.mention for role in exempt_roles if role) if exempt_roles else "None",
            inline=True
        )

        embed.add_field(
            name="💬 Exempt Channels",
            value=", ".join(channel.mention for channel in exempt_channels if channel) if exempt_channels else "None",
            inline=True
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # New command: clear current AutoMod config for the guild
    @app_commands.command(name="clear_config", description="Clear the current AutoMod configuration.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @command_enabled()
    async def clear_config(self, interaction: discord.Interaction):
        applied = load_json("data/applied_presets.json")
        if str(interaction.guild.id) in applied:
            del applied[str(interaction.guild.id)]
            save_json("data/applied_presets.json", applied)
            await interaction.response.send_message("✅ AutoMod configuration cleared for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No AutoMod configuration found to clear.", ephemeral=True)

    # New command: explicitly set log channel for AutoMod alerts
    @app_commands.command(name="set_log_channel", description="Set the channel for AutoMod alerts.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @command_enabled()
    @app_commands.describe(channel="The text channel to send AutoMod alerts to")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Save this in temp data or a persistent config as you prefer
        data = get_temp_data(self.bot, interaction.user.id)
        data["log_channel"] = channel
        await interaction.response.send_message(f"✅ Log channel set to {channel.mention}. Remember to apply the AutoMod settings!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AutoModManager(bot))
