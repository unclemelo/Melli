import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import hashlib
import asyncio

# Load AutoMod preset configurations from file
try:
    with open("data/presets.json", "r") as file:
        Presets = json.load(file)
except discord.HTTPException:
    print("JSON didn't load")


def hash_preset(preset_data):
    return hashlib.sha256(json.dumps(preset_data, sort_keys=True).encode()).hexdigest()


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
            discord.SelectOption(label="Medium Security (Recommended)", description="Balanced filtering for general use")
        ]
        super().__init__(
            placeholder="Choose a security level...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
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
        user_id = interaction.user.id
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}
        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        selected_roles = [self.guild.get_role(int(role_id)) for role_id in self.values]
        interaction.client.temp_data[user_id]["exempt_roles"] = selected_roles
        await interaction.response.send_message("✅ Exempt roles updated!", ephemeral=True)


class AutoModChannelSelector(discord.ui.Select):
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
        user_id = interaction.user.id
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}
        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        selected_channels = [self.guild.get_channel(int(channel_id)) for channel_id in self.values]
        interaction.client.temp_data[user_id]["exempt_channels"] = selected_channels
        await interaction.response.send_message("✅ Exempt channels updated!", ephemeral=True)


class TextFallbackButton(discord.ui.Button):
    def __init__(self, config_type: str):
        label = f"Enter {config_type} manually"
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=config_type)
        self.config_type = config_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✏️ Please enter the {self.config_type} manually by mentioning them (e.g., @Role or #channel). Use `/set_{self.config_type}`.",
            ephemeral=True
        )


class SaveAutoModConfigButton(discord.ui.Button):
    def __init__(self, log_channel: discord.TextChannel):
        super().__init__(label="Apply AutoMod Settings", style=discord.ButtonStyle.success)
        self.log_channel = log_channel

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        bot = interaction.client
        guild = interaction.guild

        await interaction.response.defer(ephemeral=True)
        user_temp_data = bot.temp_data.get(user_id, {})

        selected_preset = user_temp_data.get("preset")
        rule_data = Presets.get(selected_preset, {})

        rule_name = rule_data.get("rule_name", "AutoMod Rule")
        keyword_filter = rule_data.get("keyword_filter", [])
        RegExs_list = rule_data.get("regex_patterns", [])
        AllowList = rule_data.get("allowed_keywords", [])

        exempt_roles = [r for r in user_temp_data.get("exempt_roles", []) if r is not None]
        exempt_channels = [c for c in user_temp_data.get("exempt_channels", []) if c is not None]

        try:
            # Check for existing AutoMod rule with the same name
            existing_rules = await guild.fetch_automod_rules()
            existing = discord.utils.get(existing_rules, name=rule_name)

            if existing:
                await existing.edit(
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
                    reason="AutoMod rule updated by bot"
                )
                print("Updated existing rules")
            else:
                await guild.create_automod_rule(
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
                    reason="AutoMod rule created by bot"
                )


            embed = discord.Embed(
                title="✅ AutoMod Settings Applied",
                description=f"AutoMod is now using the **{selected_preset}** security level.",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)

            with open("data/applied_presets.json", "r") as f:
                applied = json.load(f)
            applied[str(guild.id)] = {
                "preset": selected_preset,
                "hash": hash_preset(rule_data)
            }
            with open("data/applied_presets.json", "w") as f:
                json.dump(applied, f, indent=4)

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
            with open("data/applied_presets.json", "r") as f:
                applied = json.load(f)
            with open("data/presets.json", "r") as f:
                current = json.load(f)
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
                    # You can call a refactored method here to apply settings.
                    applied[str(guild.id)]["hash"] = new_hash
                except Exception as e:
                    print(f"Failed to DM owner of {guild.name}: {e}")

        with open("data/applied_presets.json", "w") as f:
            json.dump(applied, f, indent=4)

    @app_commands.command(name="setup", description="Interactively set up AutoMod for your server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_automod(self, interaction: discord.Interaction):
        log_channel = discord.utils.get(interaction.guild.text_channels, name="mod-logs") or interaction.channel
        view = AutoModSettingsView(log_channel, interaction.guild)
        await interaction.response.send_message(
            "🔧 Use the menu below to configure AutoMod settings.", 
            view=view,
            ephemeral=True
        )


    @app_commands.command(name="force_update", description="Manually update the AutoMod preset.")
    @app_commands.checks.has_permissions(administrator=True)
    async def force_update(self, interaction: discord.Interaction):
        guild = interaction.guild
        try:
            with open("data/applied_presets.json", "r") as f:
                applied = json.load(f)
            with open("data/presets.json", "r") as f:
                current = json.load(f)

            settings = applied.get(str(guild.id))
            if not settings:
                await interaction.response.send_message("❌ No preset applied yet.", ephemeral=True)
                return

            preset_name = settings["preset"]
            new_data = current.get(preset_name)
            new_hash = hash_preset(new_data)

            # Apply new rule logic (refactor from button if needed)
            settings["hash"] = new_hash
            with open("data/applied_presets.json", "w") as f:
                json.dump(applied, f, indent=4)

            await interaction.response.send_message(f"✅ AutoMod preset **{preset_name}** manually updated!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AutoModManager(bot))
