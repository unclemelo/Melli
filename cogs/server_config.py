import discord
from discord import app_commands
from discord.ext import commands
from util.command_checks import get_guild_config, toggle_command, update_commands_for_guild  # Import utils

class ServerConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="command_config", description="Enable or disable commands for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_cmd(self, interaction: discord.Interaction):
        """Shows a dropdown menu to enable/disable commands."""
        guild_id = interaction.guild_id
        if guild_id is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        guild_config = get_guild_config(guild_id)

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
                    toggle_command(guild_id, selected_cmd, new_status)  # Update the config

                await interaction.response.edit_message(content="✅ Updated command settings!", view=None)

        view = discord.ui.View()
        view.add_item(CommandSelect())
        view.cog = self  # Link cog to the view

        embed = discord.Embed(title="Command Configuration",
                              description="Select commands to toggle on/off for this server.",
                              color=discord.Color.blue())
        embed.set_footer(text="Currently under maintenance.")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def cog_load(self):
        """Sync all commands when the cog is loaded."""
        for guild in self.bot.guilds:
            await update_commands_for_guild(self.bot, guild.id)

async def setup(bot: commands.Bot):
    cog = ServerConfig(bot)
    await bot.add_cog(cog)
