import json
import discord
from discord.ext import commands
from discord import app_commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/AM_regex.json"
        self.admin_role_id = 1312236793730437130
        self.load_config()

    def load_config(self):
        """Load the configuration from the JSON file."""
        try:
            with open(self.config_file, "r") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = {
                "blocked_links_regex": [],
                "allowed_links": []
            }
            self.save_config()

    def save_config(self):
        """Save the current configuration to the JSON file."""
        with open(self.config_file, "w") as file:
            json.dump(self.config, file, indent=4)

    async def has_admin_role(self, interaction: discord.Interaction) -> bool:
        """Check if the user has the admin role."""
        role = discord.utils.get(interaction.user.roles, id=self.admin_role_id)
        return role is not None

    async def admin_only_check(self, interaction: discord.Interaction):
        """Ensure the user has the required admin role."""
        if not await self.has_admin_role(interaction):
            await interaction.response.send_message(
                "You do not have the required role to use this command.",
                ephemeral=True,
            )
            return False
        return True

    # View Blocked Regex or Links
    @app_commands.command(name="view_blocked", description="View blocked regex patterns or allowed links.")
    @app_commands.choices(tool=[
        app_commands.Choice(name="Regex", value="regex"),
        app_commands.Choice(name="Links", value="links"),
    ])
    async def view_blocked(self, interaction: discord.Interaction, tool: app_commands.Choice[str]):
        """View blocked regex patterns or allowed links."""
        if tool.value == "regex":
            blocked = "\n".join(self.config["blocked_links_regex"]) or "No blocked regex patterns."
            await interaction.response.send_message(f"Blocked Regex Patterns:\n```{blocked}```")
        elif tool.value == "links":
            allowed = "\n".join(self.config["allowed_links"]) or "No allowed links."
            await interaction.response.send_message(f"Allowed Links:\n```{allowed}```")

    # Add Blocked Regex or Allowed Link
    @app_commands.command(name="add_blocked", description="Add a new blocked regex or allowed link.")
    @app_commands.choices(tool=[
        app_commands.Choice(name="Regex", value="regex"),
        app_commands.Choice(name="Link", value="link"),
    ])
    async def add_blocked(self, interaction: discord.Interaction, tool: app_commands.Choice[str], value: str):
        """Add a new blocked regex pattern or allowed link."""
        if not await self.admin_only_check(interaction):
            return

        if tool.value == "regex":
            if value in self.config["blocked_links_regex"]:
                await interaction.response.send_message("This regex pattern is already blocked.", ephemeral=True)
            else:
                self.config["blocked_links_regex"].append(value)
                self.save_config()
                await interaction.response.send_message(f"Added blocked regex pattern: `{value}`", ephemeral=True)
        elif tool.value == "link":
            if value in self.config["allowed_links"]:
                await interaction.response.send_message("This link is already allowed.", ephemeral=True)
            else:
                self.config["allowed_links"].append(value)
                self.save_config()
                await interaction.response.send_message(f"Added allowed link: `{value}`", ephemeral=True)

    # Remove Blocked Regex or Allowed Link
    @app_commands.command(name="remove_blocked", description="Remove a blocked regex or allowed link.")
    @app_commands.choices(tool=[
        app_commands.Choice(name="Regex", value="regex"),
        app_commands.Choice(name="Link", value="link"),
    ])
    async def remove_blocked(self, interaction: discord.Interaction, tool: app_commands.Choice[str], value: str):
        """Remove a blocked regex pattern or allowed link."""
        if not await self.admin_only_check(interaction):
            return

        if tool.value == "regex":
            if value not in self.config["blocked_links_regex"]:
                await interaction.response.send_message("This regex pattern is not in the blocked list.", ephemeral=True)
            else:
                self.config["blocked_links_regex"].remove(value)
                self.save_config()
                await interaction.response.send_message(f"Removed blocked regex pattern: `{value}`", ephemeral=True)
        elif tool.value == "link":
            if value not in self.config["allowed_links"]:
                await interaction.response.send_message("This link is not in the allowed list.", ephemeral=True)
            else:
                self.config["allowed_links"].remove(value)
                self.save_config()
                await interaction.response.send_message(f"Removed allowed link: `{value}`", ephemeral=True)

# Setup the Cog
async def setup(bot):
    await bot.add_cog(AutoMod(bot))
