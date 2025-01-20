import discord
from discord import app_commands
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        

    @app_commands.command(name="ban", description="Bans a user.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str):
        try:
            embed = discord.Embed(title=f"X3 {member.name} was hit with the Melon Hammer! <:Melonbanned:1294154990939537518>")
            await interaction.response.send_message(embed=embed)
            await member.ban(reason=reason)
        except:
            await interaction.response.send_message(f"We could not ban {member.name}...")
    
    @app_commands.command(name="kick", description="Kicks a user.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_cmd(self, interaction: discord.Interaction, member: discord.Member, *, reason: str):
        try:
            embed = discord.Embed(title=f"X3 {member.name} was hit with the Melon Hammer! <:Melonbanned:1294154990939537518>")
            await interaction.response.send_message(embed=embed)
            await member.kick(reason=reason)
        except:
            await interaction.response.send_message(f"We could not kick {member.name}...")






        

async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))
