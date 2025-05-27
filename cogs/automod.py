import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import hashlib
import re
from util.command_checks import command_enabled
from util.automod import (
    hash_preset, get_temp_data, load_json, save_json, apply_automod_rule
)

Presets = load_json("data/presets.json")
ID_EXTRACTOR = re.compile(r"<@&?(\d+)>|(\d+)")

# --- Modal Inputs ---

class ManualInputModal(discord.ui.Modal):
    def __init__(self, guild: discord.Guild, input_type: str):
        title = f"Enter exempt {input_type} manually"
        super().__init__(title=title)
        self.guild = guild
        self.input_type = input_type
        self.input_field = discord.ui.TextInput(
            label=f"{input_type.capitalize()}s (mention or ID, space/comma separated)",
            style=discord.TextStyle.paragraph,
            placeholder="@Moderator, 123456789012345678",
            required=True,
            max_length=400
        )
        self.add_item(self.input_field)

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.input_field.value
        ids = set()
        for part in re.split(r"[\s,]+", raw):
            if not part.strip():
                continue
            match = ID_EXTRACTOR.match(part)
            if match:
                id_val = int(match.group(1) or match.group(2))
                if self.input_type == "roles" and self.guild.get_role(id_val):
                    ids.add(id_val)
                elif self.input_type == "channels" and self.guild.get_channel(id_val):
                    ids.add(id_val)
        
        data = get_temp_data(interaction.client, interaction.user.id)
        if self.input_type == "roles":
            data["exempt_roles"] = [self.guild.get_role(rid) for rid in ids if self.guild.get_role(rid)]
        else:
            data["exempt_channels"] = [self.guild.get_channel(cid) for cid in ids if self.guild.get_channel(cid)]

        await interaction.response.send_message(
            f"✅ Exempt {self.input_type} manually updated ({len(ids)} {self.input_type}).",
            ephemeral=True
        )

# --- UI Selects ---

class AutoModPresetSelector(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=data.get("description", "No description"))
            for name, data in Presets.items()
        ]
        super().__init__(placeholder="Choose a security level...", options=options)

    async def callback(self, interaction: discord.Interaction):
        data = get_temp_data(interaction.client, interaction.user.id)
        selected = self.values[0]
        data["preset"] = selected
        data["config"] = Presets.get(selected, {})
        await interaction.response.send_message(f"✅ Preset **{selected}** selected!", ephemeral=True)

class ExemptSelector(discord.ui.Select):
    def __init__(self, items, item_type: str, guild: discord.Guild):
        options = [discord.SelectOption(label=item.name, value=str(item.id)) for item in items]
        placeholder = f"Choose exempt {item_type}..."
        super().__init__(placeholder=placeholder, options=options, min_values=0, max_values=len(options))
        self.item_type = item_type
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        data = get_temp_data(interaction.client, interaction.user.id)
        if self.item_type == "roles":
            data["exempt_roles"] = [self.guild.get_role(int(val)) for val in self.values]
        else:
            data["exempt_channels"] = [self.guild.get_channel(int(val)) for val in self.values]
        await interaction.response.send_message(f"✅ Exempt {self.item_type} updated!", ephemeral=True)

# --- Buttons ---

class ManualInputButton(discord.ui.Button):
    def __init__(self, item_type: str, guild: discord.Guild):
        super().__init__(label=f"Enter {item_type} manually", style=discord.ButtonStyle.secondary)
        self.item_type = item_type
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ManualInputModal(self.guild, self.item_type))

class SaveConfigButton(discord.ui.Button):
    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(label="Apply AutoMod Settings", style=discord.ButtonStyle.success)
        self.log_channel = log_channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = get_temp_data(interaction.client, interaction.user.id)
        rule_data = data.get("config", {})
        roles = data.get("exempt_roles", [])
        channels = data.get("exempt_channels", [])

        await apply_automod_rule(interaction.guild, self.log_channel, rule_data, roles, channels)

        embed = discord.Embed(title="✅ AutoMod Settings Applied",
                              description=f"Using **{data.get('preset')}** preset.",
                              color=discord.Color.magenta())

        def field_val(lst, fmt=str): return ", ".join(map(fmt, lst)) if lst else "None"

        embed.add_field(name="🧠 Regex", value=f"```\n{chr(10).join(rule_data.get('regex_patterns', []))}```" or "None", inline=False)
        embed.add_field(name="📝 Blocked Keywords", value=field_val(rule_data.get("keyword_filter", [])), inline=False)
        embed.add_field(name="🚫 Allowed Keywords", value=field_val(rule_data.get("allowed_keywords", [])), inline=False)
        embed.add_field(name="🎭 Exempt Roles", value=field_val(roles, lambda r: r.mention if r else ""), inline=True)
        embed.add_field(name="💬 Exempt Channels", value=field_val(channels, lambda c: c.mention if c else ""), inline=True)
        embed.set_footer(text=f"📢 Alerts sent to: #{self.log_channel.name}")

        await interaction.followup.send(embed=embed)

        applied = load_json("data/applied_presets.json")
        applied[str(interaction.guild.id)] = {"preset": data.get("preset"), "hash": hash_preset(rule_data)}
        save_json("data/applied_presets.json", applied)

# --- View ---

class AutoModSettingsView(discord.ui.View):
    def __init__(self, log_channel: discord.TextChannel, guild: discord.Guild):
        super().__init__(timeout=None)
        self.add_item(AutoModPresetSelector())

        role_items = [r for r in guild.roles if r.name != "@everyone"]
        if len(role_items) <= 25:
            self.add_item(ExemptSelector(role_items, "roles", guild))
        else:
            self.add_item(ManualInputButton("roles", guild))

        text_channels = guild.text_channels
        if len(text_channels) <= 25:
            self.add_item(ExemptSelector(text_channels, "channels", guild))
        else:
            self.add_item(ManualInputButton("channels", guild))

        self.add_item(SaveConfigButton(log_channel))


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
