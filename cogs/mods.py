import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Mod(commands.Cog):
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

    @app_commands.command(name="mute", description="Temporarily mutes a user using Discord's timeout feature.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_cmd(self, interaction: discord.Interaction, member: discord.Member, time: int, *, reason: str = "No reason provided"):
        try:
            # Apply timeout
            timeout_duration = timedelta(minutes=time)
            await member.edit(timeout_until=discord.utils.utcnow() + timeout_duration, reason=reason)
            
            embed = discord.Embed(
                title=f"🤐 {member.name} has been muted!",
                description=f"Reason: {reason}\nDuration: {time} minutes.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Hmm... couldn't mute {member.name}. Did they dodge the timeout? 🕵️\nError: {str(e)}")

    @app_commands.command(name="unmute", description="Removes a user's mute (timeout).")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute_cmd(self, interaction: discord.Interaction, member: discord.Member):
        try:
            # Remove timeout
            await member.edit(timeout_until=None)
            
            embed = discord.Embed(
                title=f"🔊 {member.name} has been unmuted!",
                description="They can now speak freely... for better or worse. 🤔",
                color=discord.Color.green()# colour
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Couldn't unmute {member.name}. Are they already unmuted? 🤷\nError: {str(e)}")

    @app_commands.command(name="clear", description="Clears a number of messages.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_cmd(self, interaction: discord.Interaction, amount: int):
        try:
            await interaction.channel.purge(limit=amount)
            await interaction.response.send_message(f"🧹 Poof! Cleared {amount} messages. The chat looks spotless now!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Yikes! Couldn't clear messages. Is the vacuum broken? 🧼\nError: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))

