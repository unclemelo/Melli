import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="kick", description="Kicks a user.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        try:
            embed = discord.Embed(
                title=f"🥾 **{member.name} was yeeted out of the server!**",
                description=f"Reason: {reason}\nFly safe, traveler. 🚀",
                color=discord.Color.orange()
            )
            await member.kick(reason=reason)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Oops! Couldn't kick {member.name}. Maybe they bribed the mods? 🧐\nError: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Kick(bot))

