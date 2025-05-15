import discord
from discord import app_commands
from discord.ext import commands
from util.command_checks import get_guild_config, toggle_command, update_commands_for_guild

COMMANDS_PER_PAGE = 25

class ServerConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="command_config", description="Enable or disable commands for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_cmd(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if guild_id is None:
            return await interaction.response.send_message("⚠️ This command can only be used in a server.", ephemeral=True)

        guild_config = get_guild_config(guild_id)

        all_cmds = {
            cmd.name: guild_config.get(cmd.name, True)
            for cmd in self.bot.tree.get_commands()
            if cmd.name != "command_config"
        }

        sorted_cmds = sorted(all_cmds.items())

        class CommandToggleView(discord.ui.View):
            def __init__(self, page: int = 0):
                super().__init__(timeout=180)
                self.page = page
                self.max_pages = (len(sorted_cmds) - 1) // COMMANDS_PER_PAGE
                self.last_user = interaction.user.id
                self.update_select()

            def update_select(self):
                self.clear_items()

                start = self.page * COMMANDS_PER_PAGE
                end = start + COMMANDS_PER_PAGE
                cmds = sorted_cmds[start:end]

                options = [
                    discord.SelectOption(
                        label=name,
                        description="Enabled" if enabled else "Disabled",
                        value=name
                    ) for name, enabled in cmds
                ]

                self.add_item(self.CommandSelect(options))

                if self.max_pages > 0:
                    self.add_item(self.BackButton())
                    self.add_item(self.NextButton())

                self.add_item(self.RefreshButton())
                self.add_item(self.SearchButton())

            async def interaction_check(self, i: discord.Interaction) -> bool:
                if i.user.id != self.last_user:
                    await i.response.send_message("Only the person who ran this command can interact with it.", ephemeral=True)
                    return False
                return True

            class CommandSelect(discord.ui.Select):
                def __init__(self, options):
                    super().__init__(
                        placeholder="Select commands to toggle",
                        min_values=1,
                        max_values=len(options),
                        options=options
                    )

                async def callback(self, interaction: discord.Interaction):
                    updated = []
                    for cmd_name in self.values:
                        new_status = not all_cmds[cmd_name]
                        toggle_command(guild_id, cmd_name, new_status)
                        all_cmds[cmd_name] = new_status
                        updated.append(f"`{cmd_name}` → {'✅ Enabled' if new_status else '❌ Disabled'}")

                    await interaction.response.send_message(
                        "### 🔧 Command Settings Updated:\n" + "\n".join(updated),
                        ephemeral=True
                    )

            class BackButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="⬅ Back", style=discord.ButtonStyle.secondary)

                async def callback(self, interaction: discord.Interaction):
                    if view.page > 0:
                        view.page -= 1
                        view.update_select()
                        await interaction.response.edit_message(view=view)

            class NextButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="Next ➡", style=discord.ButtonStyle.secondary)

                async def callback(self, interaction: discord.Interaction):
                    if view.page < view.max_pages:
                        view.page += 1
                        view.update_select()
                        await interaction.response.edit_message(view=view)

            class RefreshButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="🔄 Refresh", style=discord.ButtonStyle.primary)

                async def callback(self, interaction: discord.Interaction):
                    self.view.update_select()
                    await interaction.response.edit_message(view=self.view)

            class SearchButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="🔍 Search", style=discord.ButtonStyle.success)

                async def callback(self, interaction: discord.Interaction):
                    await interaction.response.send_modal(SearchModal())

        class SearchModal(discord.ui.Modal, title="Search Command to Toggle"):
            name = discord.ui.TextInput(
                label="Command Name",
                placeholder="e.g. ban, kick, ping",
                required=True,
                min_length=1,
                max_length=32
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                cmd_name = self.name.value.strip().lower()
                if cmd_name not in all_cmds:
                    return await modal_interaction.response.send_message(
                        f"❌ Command `{cmd_name}` not found.", ephemeral=True
                    )

                new_status = not all_cmds[cmd_name]
                toggle_command(guild_id, cmd_name, new_status)
                all_cmds[cmd_name] = new_status
                await modal_interaction.response.send_message(
                    f"✅ `{cmd_name}` is now {'enabled' if new_status else 'disabled'}.",
                    ephemeral=True
                )

        embed = discord.Embed(
            title="🛠 Command Configuration",
            description="Toggle commands on/off for this server.\nYou can also search by name or navigate pages.",
            color=discord.Color.magenta()
        )
        embed.set_footer(text="Changes apply immediately • Ephemeral only")

        view = CommandToggleView()
        view.cog = self

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def cog_load(self):
        for guild in self.bot.guilds:
            await update_commands_for_guild(self.bot, guild.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerConfig(bot))
