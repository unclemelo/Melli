import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import hashlib
from util.command_checks import command_enabled

# Utility functions

def hash_preset(preset_data):
    return hashlib.sha256(json.dumps(preset_data, sort_keys=True).encode()).hexdigest()

def get_temp_data(bot, user_id):
    if not hasattr(bot, "temp_data"):
        bot.temp_data = {}
    return bot.temp_data.setdefault(user_id, {})

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

async def apply_automod_rule(guild, log_channel, rule_data, exempt_roles, exempt_channels, reason="AutoMod update"):
    rule_name = rule_data.get("rule_name", "AutoMod Rule")
    keyword_filter = rule_data.get("keyword_filter", [])
    regex_patterns = rule_data.get("regex_patterns", [])
    allow_list = rule_data.get("allowed_keywords", [])

    existing_rules = await guild.fetch_automod_rules()
    existing = discord.utils.get(existing_rules, name=rule_name)

    actions = [
        discord.AutoModRuleAction(type=discord.AutoModRuleActionType.send_alert_message, channel_id=log_channel.id),
        discord.AutoModRuleAction(type=discord.AutoModRuleActionType.block_message)
    ]

    trigger = discord.AutoModTrigger(
        type=discord.AutoModRuleTriggerType.keyword,
        keyword_filter=keyword_filter,
        allow_list=allow_list,
        regex_patterns=regex_patterns,
    )

    if existing:
        await existing.edit(trigger=trigger, actions=actions, enabled=True, exempt_roles=exempt_roles, exempt_channels=exempt_channels, reason=reason)
    else:
        await guild.create_automod_rule(
            name=rule_name,
            event_type=discord.AutoModRuleEventType.message_send,
            trigger=trigger,
            actions=actions,
            enabled=True,
            exempt_roles=exempt_roles,
            exempt_channels=exempt_channels,
            reason=reason
        )

# Load presets
Presets = load_json("data/presets.json")

class AutoModSettingsView(discord.ui.View):
    def __init__(self, log_channel: discord.TextChannel, guild: discord.Guild):
        super().__init__(timeout=None)
        self.add_item(AutoModPresetSelector())

        if len(guild.roles) <= 23:
            self.add_item(AutoModRoleSelector(guild))
        else:
            self.add_item(TextFallbackButton("roles"))

        if len(guild.text_channels) <= 23:
            self.add_item(AutoModChannelSelector(guild))
        else:
            self.add_item(TextFallbackButton("channels"))

        self.add_item(SaveAutoModConfigButton(log_channel))

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

class TextFallbackButton(discord.ui.Button):
    def __init__(self, config_type: str):
        super().__init__(label=f"Enter {config_type} manually", style=discord.ButtonStyle.secondary, custom_id=config_type)
        self.config_type = config_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✏️ Please enter the {self.config_type} manually by mentioning them. Use `/set_{self.config_type}`.", ephemeral=True
        )

class SaveAutoModConfigButton(discord.ui.Button):
    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(label="Apply AutoMod Settings", style=discord.ButtonStyle.success)
        self.log_channel = log_channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = get_temp_data(interaction.client, interaction.user.id)

        try:
            rule_data = data.get("config", {})
            await apply_automod_rule(interaction.guild, self.log_channel, rule_data, data.get("exempt_roles", []), data.get("exempt_channels", []))

            embed = discord.Embed(title="✅ AutoMod Settings Applied", description=f"AutoMod is now using the **{data.get('preset')}** preset.", color=discord.Color.green())
            await interaction.followup.send(embed=embed)

            applied = load_json("data/applied_presets.json")
            applied[str(interaction.guild.id)] = {"preset": data.get("preset"), "hash": hash_preset(rule_data)}
            save_json("data/applied_presets.json", applied)

        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed to create AutoMod rule: {e}", ephemeral=True)

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
                    await guild.owner.send(f"🔄 AutoMod preset '{preset_name}' has changed and was auto-updated on {guild.name}.")
                    applied[str(guild.id)]["hash"] = new_hash
                except Exception as e:
                    print(f"Failed to DM owner of {guild.name}: {e}")

        save_json("data/applied_presets.json", applied)

    @app_commands.command(name="setup", description="Interactively set up AutoMod for your server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @command_enabled()
    async def setup_automod(self, interaction: discord.Interaction):
        log_channel = discord.utils.get(interaction.guild.text_channels, name="mod-logs") or interaction.channel
        view = AutoModSettingsView(log_channel, interaction.guild)
        await interaction.response.send_message("🔧 Use the menu below to configure AutoMod settings.", view=view, ephemeral=True)

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

async def setup(bot):
    await bot.add_cog(AutoModManager(bot))
