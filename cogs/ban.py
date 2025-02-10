import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from datetime import timedelta


class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bans a user.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        try:
            embed = discord.Embed(
                title=f"🔨 **{member.name} was struck by the Melon Hammer!**",
                description=f"Reason: {reason}\nThey had it coming!",
                color=discord.Color.red()
            )
            await member.ban(reason=reason)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Oops! Couldn't ban {member.name}. Did they dodge the hammer? 😳\nError: {str(e)}")

    @app_commands.command(name="unban", description="Unbans a user.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_cmd(self, interaction: discord.Interaction, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title=f"✨ {user.name} is free from ban jail!",
                description="Let's hope they behave this time. 🤔",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Hmm... couldn't unban that user. Are you sure they're banned? 😅\nError: {str(e)}")

    

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))

