import discord
from discord.ext import commands
from discord import app_commands
from util.command_checks import command_enabled

class VCTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Move member to another VC
    @app_commands.command(name="move", description="Move a member to another voice channel.")
    @app_commands.checks.has_permissions(move_members=True)
    @command_enabled()
    async def move(self, interaction: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
        if not member.voice:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="⚠️ Not in Voice",
                    description=f"{member.mention} is not in a voice channel.",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )
        
        await member.move_to(channel)
        embed = discord.Embed(
            title="🔀 Member Moved",
            description=f"{member.mention} has been moved to **{channel.name}**.",
            color=discord.Color.magenta()
        )
        await interaction.response.send_message(embed=embed)

    # Server mute
    @app_commands.command(name="vc_mute", description="Server mute a member in VC.")
    @app_commands.checks.has_permissions(mute_members=True)
    @command_enabled()
    async def vcmute(self, interaction: discord.Interaction, member: discord.Member):
        if not member.voice:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="⚠️ Not in Voice",
                    description=f"{member.mention} is not in a voice channel.",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )
        
        await member.edit(mute=True)
        embed = discord.Embed(
            title="🔇 Member Muted",
            description=f"{member.mention} has been server muted.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="vc_unmute", description="Unmute a member in VC.")
    @app_commands.checks.has_permissions(mute_members=True)
    @command_enabled()
    async def vcunmute(self, interaction: discord.Interaction, member: discord.Member):
        if not member.voice:
            return await interaction.response.send_message(embed=self._not_in_vc(member), ephemeral=True)
        await member.edit(mute=False)
        embed = discord.Embed(
            title="🔊 Member Unmuted",
            description=f"{member.mention} has been unmuted.",
            color=discord.Color.magenta()
        )
        await interaction.response.send_message(embed=embed)

    # Server deafen
    @app_commands.command(name="deafen", description="Server deafen a member in VC.")
    @app_commands.checks.has_permissions(deafen_members=True)
    @command_enabled()
    async def deafen(self, interaction: discord.Interaction, member: discord.Member):
        if not member.voice:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="⚠️ Not in Voice",
                    description=f"{member.mention} is not in a voice channel.",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )
        
        await member.edit(deafen=True)
        embed = discord.Embed(
            title="🔕 Member Deafened",
            description=f"{member.mention} has been server deafened.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="undeafen", description="Undeafen a member in VC.")
    @app_commands.checks.has_permissions(deafen_members=True)
    @command_enabled()
    async def undeafen(self, interaction: discord.Interaction, member: discord.Member):
        if not member.voice:
            return await interaction.response.send_message(embed=self._not_in_vc(member), ephemeral=True)
        await member.edit(deafen=False)
        embed = discord.Embed(
            title="🔔 Member Undeafened",
            description=f"{member.mention} has been undeafened.",
            color=discord.Color.magenta()
        )
        await interaction.response.send_message(embed=embed)

    # Kick member from VC (move to None)
    @app_commands.command(name="kickvc", description="Remove a member from their voice channel.")
    @app_commands.checks.has_permissions(move_members=True)
    @command_enabled()
    async def kickvc(self, interaction: discord.Interaction, member: discord.Member):
        if not member.voice:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="⚠️ Not in Voice",
                    description=f"{member.mention} is not in a voice channel.",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )
        
        await member.move_to(None)
        embed = discord.Embed(
            title="🚪 Member Removed from VC",
            description=f"{member.mention} has been kicked from the voice channel.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(VCTools(bot))
