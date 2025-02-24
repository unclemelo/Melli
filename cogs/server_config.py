import discord
from discord import app_commands
from discord.ext import commands
import json

class ServerConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # to do: make it a selection to pick out of all the cmds and set their value to True/False
    @app_commands.command(name="Command config", description="Changes what commands are allowed on a server")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_cmd(self, interaction: discord.Interaction):
        """Set the server-specific comand to true/false"""
        try:
            embed = discord.Embed(title="Server commands permissions",description="cmd - number\ncmd - number",color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Couldent load server specific cmds \nError: {str(e)}")
    
async def setup(bot: commands.Bot):
    await bot.add_cog(ServerConfig(bot))