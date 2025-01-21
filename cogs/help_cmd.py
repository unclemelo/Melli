import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from colorama import Fore

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows the list of commands")
    async def helpcmd(self, interaction: discord.Interaction):
        """Show list of cmds"""
        try:
            cmd_list=["/ban", "/chaos", "/clear", "/clearwarns", "/delwarn", "/kick",  "/knockout", 
                      "/mute", "/prank", "/reboot", "/revive", "/setup_automod", "/shutdown", "/unban", 
                      "/unmute", "/update_automod", "/uptime", "/votekick", "/warn", "/warnings"]
            cmd_list="\n".join(cmd_list)
            await interaction.response.send_message(f"List of comands:\n{cmd_list}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred. Please contact an administrator.\n```{e}```", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))