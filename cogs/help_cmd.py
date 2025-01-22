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
            cmd_list=", ".join(["/ban", "/chaos", "cheese", "/clear", "/clearwarns", "/delwarn", "/kick",  "/knockout", 
                      "/mute", "/prank", "/reboot", "/revive", "/setup_automod", "/shutdown", "/unban", 
                      "/unmute", "/update_automod", "/uptime", "/votekick", "/warn", "/warnings"])
            
            embed = discord.Embed(title="List of Commands", description=f"{cmd_list}", color=0x3474eb)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred. Please contact an administrator.\n```{e}```", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))