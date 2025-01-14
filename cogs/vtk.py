import discord
import asyncio
from discord.ext import commands
from discord import app_commands

class VoteToKick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vote_sessions = {}  # Dictionary to track ongoing vote sessions

    @app_commands.command(name="votekick", description="Vote to kick annoying people from the server!")
    @app_commands.checks.cooldown(1, 43200, key=lambda i: (i.guild.id))  # 12-hour cooldown
    async def votekick(self, interaction: discord.Interaction, member: discord.Member):
        """Starts a vote to kick a specified member."""

        # Check if the target has moderation permissions
        if member.guild_permissions.manage_messages or member.guild_permissions.kick_members:
            embed = discord.Embed(
                description=f"{member.mention} has moderation permissions and cannot be kicked.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Prevent duplicate vote sessions for the same user
        if member.id in self.vote_sessions:
            embed = discord.Embed(
                description=f"A vote to kick {member.mention} is already ongoing!",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Initialize vote session
        self.vote_sessions[member.id] = {
            "votes": 0,
            "timeout": asyncio.create_task(self.vote_timeout(interaction, member)),
        }

        embed = discord.Embed(
            title=f"Vote to Kick {member.mention}",
            description=f"A vote to kick {member.mention} has started! React with ✅ to vote YES. Voting ends in 2 minutes.",
            color=discord.Color.green()
        )
        vote_message = await interaction.response.send_message(embed=embed, ephemeral=False)
        vote_message = await interaction.original_response()

        # React to message
        await vote_message.add_reaction("\u2705")

        # Wait for reactions
        def check(reaction, user):
            return (
                reaction.message.id == vote_message.id
                and str(reaction.emoji) == "\u2705"
                and user != self.bot.user
                and not user.guild_permissions.manage_messages
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                # Increment vote count and notify
                self.vote_sessions[member.id]["votes"] += 1
                embed = discord.Embed(
                    description=f"{user.mention} voted YES. Total votes: {self.vote_sessions[member.id]['votes']}.",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=embed)

                # Check if votes are enough to kick (50% +1 of server members)
                if self.vote_sessions[member.id]["votes"] >= len(interaction.guild.members) // 2 + 1:
                    embed = discord.Embed(
                        description=f"Vote passed! {member.mention} will be kicked.",
                        color=discord.Color.green()
                    )
                    await interaction.followup.send(embed=embed)
                    await member.kick(reason="Vote-kicked by server members.")
                    self.vote_sessions[member.id]["timeout"].cancel()
                    del self.vote_sessions[member.id]
                    break
            except asyncio.TimeoutError:
                break

    async def vote_timeout(self, interaction: discord.Interaction, member: discord.Member):
        """Handles vote timeout."""
        await asyncio.sleep(120)  # 2-minutes timeout

        # Check if vote session is still active
        if member.id in self.vote_sessions:
            votes = self.vote_sessions[member.id]["votes"]
            embed = discord.Embed(
                description=f"Vote to kick {member.mention} has ended. Total votes: {votes}. Not enough votes to kick.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            del self.vote_sessions[member.id]

async def setup(bot: commands.Bot):
    await bot.add_cog(VoteToKick(bot))
