import discord
from discord.ext import commands
from discord import app_commands

class SlashCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="list_slash_commands", description="Lists all synced slash commands.")
    async def list_slash_commands(self, interaction: discord.Interaction):
        """Lists all synced slash commands."""
        # Fetch global commands
        global_commands = await self.bot.tree.fetch()
        response = "**Global Slash Commands:**\n"
        if global_commands:
            for command in global_commands:
                response += f"- `{command.name}`: {command.description}\n"
        else:
            response += "No global slash commands found.\n"

        # Optionally, include guild-specific commands
        for guild in self.bot.guilds:
            guild_commands = await self.bot.tree.fetch_guild_commands(guild_id=guild.id)
            if guild_commands:
                response += f"\n**Guild-specific Slash Commands for `{guild.name}`:**\n"
                for command in guild_commands:
                    response += f"- `{command.name}`: {command.description}\n"

        # Send response
        await interaction.response.send_message(response, ephemeral=True)

async def setup(bot: commands.Bot):
    """Loads the SlashCommandsCog."""
    await bot.add_cog(SlashCommandsCog(bot))
