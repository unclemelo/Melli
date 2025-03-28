import discord
from discord import app_commands
from discord.ext import commands
import json
from util.command_checks import is_command_enabled
# Load AutoMod preset configurations from file

"""Load AutoMod presets from the given JSON file."""
try:
    with open("data/presets.json", "r") as file:
     Presets = json.load(file)
except discord.HTTPException as e:
    # Return an empty dict if file is not found or invalid JSON
    print("JSON didnt load")

class PaginatedSelectView(discord.ui.View):
    def __init__(self, items, placeholder="Select an option...", max_per_page=25, timeout=60):
        super().__init__(timeout=timeout)
        self.items = items
        self.placeholder = placeholder
        self.max_per_page = max_per_page
        self.current_page = 0  # Track pagination

        self.select_menu = discord.ui.Select(placeholder=self.placeholder)
        self.update_options()  # Populate select menu
        self.add_item(self.select_menu)

        # Add pagination buttons
        self.previous_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
        self.next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary, disabled=True)

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    def update_options(self):
        """Update the select menu options based on the current page."""
        start = self.current_page * self.max_per_page
        end = start + self.max_per_page
        paginated_items = self.items[start:end]

        self.select_menu.options = [
            discord.SelectOption(label=item.name, value=str(item.id)) for item in paginated_items
        ]

        # Update button states
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = end >= len(self.items)

    async def previous_page(self, interaction: discord.Interaction):
        """Handles the previous page button."""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_options()
            await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        """Handles the next page button."""
        if (self.current_page + 1) * self.max_per_page < len(self.items):
            self.current_page += 1
            self.update_options()
            await interaction.response.edit_message(view=self)

    async def on_timeout(self):
        """Disable interactions when the view times out."""
        for child in self.children:
            child.disabled = True
        self.stop()



# UI for AutoMod settings
class AutoModSettingsView(discord.ui.View):
    """UI view that includes preset selection, role selection, channel selection, and save button for AutoMod settings."""
    def __init__(self, log_channel: discord.TextChannel, guild: discord.Guild):
        super().__init__(timeout=None)
        self.add_item(AutoModPresetSelector())  # Preset Selector

        # If PaginatedSelectView is used for roles, add it as a child View instead
        self.role_selector_view = PaginatedSelectView(guild.roles, "Choose exempt roles...", max_per_page=25)
        self.channel_selector_view = PaginatedSelectView(guild.text_channels, "Choose exempt channels...", max_per_page=25)

        self.add_item(SaveAutoModConfigButton(log_channel))  # Apply Settings Button

    async def send(self, interaction: discord.Interaction):
        """Send the main AutoMod setup view + paginated views."""
        await interaction.response.send_message(view=self)
        await interaction.followup.send(view=self.role_selector_view, ephemeral=True)  # Send roles selector
        await interaction.followup.send(view=self.channel_selector_view, ephemeral=True)  # Send channels selector




# Dropdown menu to select AutoMod presets
class AutoModPresetSelector(discord.ui.Select):
    """Dropdown menu to select the AutoMod security preset."""
    def __init__(self):
        options = [
            discord.SelectOption(label="Low Security", description="Minimal filtering for casual servers"),
            discord.SelectOption(label="Medium Security (Recommended)", description="Balanced filtering for general use"),
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
        user_id = interaction.user.id  # Track data per-user
        
        # Ensure temp storage exists and doesn't overwrite previous entries
        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}
        
        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        selected_preset = self.values[0]
        
        # Store the selected preset properly
        interaction.client.temp_data[user_id]["preset"] = selected_preset
        interaction.client.temp_data[user_id]["config"] = Presets.get(selected_preset, {})
        
        await interaction.response.send_message(f"✅ Preset **{selected_preset}** selected!", ephemeral=True)


# Dropdown menu to select exempt roles
class AutoModRoleSelector(PaginatedSelectView):
    def __init__(self, guild):
        roles = [role for role in guild.roles if role.name != "@everyone"]
        super().__init__(guild, roles, item_type="role")

    async def interaction_check(self, interaction: discord.Interaction):
        """Handle role selection."""
        user_id = interaction.user.id
        selected_roles = [self.guild.get_role(int(role_id)) for role_id in interaction.data['values']]

        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        interaction.client.temp_data[user_id]["exempt_roles"] = selected_roles
        await interaction.response.send_message(f"✅ Exempt roles updated!", ephemeral=True)


# Dropdown menu to select exempt channels
class AutoModChannelSelector(PaginatedSelectView):
    def __init__(self, guild):
        channels = [channel for channel in guild.text_channels]
        super().__init__(guild, channels, item_type="channel")

    async def interaction_check(self, interaction: discord.Interaction):
        """Handle channel selection."""
        user_id = interaction.user.id
        selected_channels = [self.guild.get_channel(int(channel_id)) for channel_id in interaction.data['values']]

        if not hasattr(interaction.client, "temp_data"):
            interaction.client.temp_data = {}

        if user_id not in interaction.client.temp_data:
            interaction.client.temp_data[user_id] = {}

        interaction.client.temp_data[user_id]["exempt_channels"] = selected_channels
        await interaction.response.send_message(f"✅ Exempt channels updated!", ephemeral=True)


# Button to save AutoMod settings
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

        # ✅ Ensure temp_data exists for the user
        user_temp_data = bot.temp_data.get(user_id, {})
        if not user_temp_data:
            await interaction.followup.send("⚠ No AutoMod settings found. Please select a preset and try again!", ephemeral=True)
            return

        # ✅ Retrieve the selected preset
        selected_preset = user_temp_data.get("preset")
        if not selected_preset:
            await interaction.followup.send("⚠ No preset selected. Please choose a preset before saving!", ephemeral=True)
            return

        # ✅ Load rule data
        rule_data = Presets.get(selected_preset, {})
        if not rule_data:
            await interaction.followup.send("⚠ Error: Preset settings not found!", ephemeral=True)
            return

        rule_name = rule_data.get("rule_name", "AutoMod Rule")
        keyword_filter = rule_data.get("keyword_filter", [])
        RegExs_list = rule_data.get("regex_patterns", [])
        AllowList = rule_data.get("allowed_keywords", [])

        # ✅ Fetch exempt roles & channels (Ensure they are valid objects)
        exempt_roles = [
            guild.get_role(int(role.id)) for role in user_temp_data.get("exempt_roles", [])
            if guild.get_role(int(role.id)) is not None
        ]
        exempt_channels = [
            guild.get_channel(int(channel.id)) for channel in user_temp_data.get("exempt_channels", [])
            if guild.get_channel(int(channel.id)) is not None
        ]

        # ✅ Validate if log_channel is set correctly
        if not self.log_channel:
            await interaction.followup.send("⚠ Log channel not found. Please try again!", ephemeral=True)
            return

        # ✅ Attempt to create the AutoMod rule
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
            embed.add_field(name="Support Server", value="Our presets are always improving, stay updated on your preset by joining the support server. [here](https://discord.gg/PD2fpwGyx6)")
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
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "automod_setup"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
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
