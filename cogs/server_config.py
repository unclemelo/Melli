import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_FILE = "data/guildConf.json"

class ServerConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load_config()

    def load_config(self):
        """Loads or creates the guildConf.json file."""
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as f:
                json.dump({"Servers": {}}, f, indent=4)
        with open(CONFIG_FILE, "r") as f:
            self.config = json.load(f)

    def save_config(self):
        """Saves the current config to the file."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_guild_config(self, guild_id: int):
        """Returns the guild's command settings, initializes if missing."""
        if str(guild_id) not in self.config["Servers"]:
            self.config["Servers"][str(guild_id)] = {}
            self.save_config()
        return self.config["Servers"][str(guild_id)]

    def toggle_command(self, guild_id: int, command: str, value: bool):
        """Enables or disables a command for the server."""
        guild_config = self.get_guild_config(guild_id)
        guild_config[command] = value
        self.config["Servers"][str(guild_id)] = guild_config
        self.save_config()

    @app_commands.command(name="command_config", description="Enable or disable commands for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_cmd(self, interaction: discord.Interaction):
        """Shows a dropdown menu to enable/disable commands."""
        guild_id = interaction.guild_id
        if guild_id is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        guild_config = self.get_guild_config(guild_id)

        # Get all commands and their current status
        all_commands = {cmd.name: guild_config.get(cmd.name, True) for cmd in self.bot.tree.get_commands()}

        class CommandSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label=cmd,
                        description="Enabled" if status else "Disabled",
                        value=cmd
                    ) for cmd, status in all_commands.items()
                ]
                super().__init__(placeholder="Select commands to toggle", min_values=1, max_values=len(options), options=options)

            async def callback(self, interaction: discord.Interaction):
                for selected_cmd in self.values:
                    new_status = not all_commands[selected_cmd]  # Toggle the value
                    self.view.cog.toggle_command(guild_id, selected_cmd, new_status)

                await interaction.response.edit_message(content="Updated command settings!", view=None)

        view = discord.ui.View()
        view.add_item(CommandSelect())
        view.cog = self  # Link cog to the view

        embed = discord.Embed(title="Command Configuration",
                              description="Select commands to toggle on/off for this server.",
                              color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerConfig(bot))
