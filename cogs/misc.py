import discord
import asyncio
import random
import json
import os
from discord.ext import commands, tasks
from discord import app_commands
from typing import List
from discord.ext.commands import cooldown, BucketType
from datetime import timedelta
from util.command_checks import is_command_enabled


class MISC(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    
    @app_commands.command(name="revive", description="Bring back a timed-out user with flair!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def revive_cmd(self, interaction: discord.Interaction, member: discord.Member):
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "revive"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
        try:
            await member.edit(timed_out_until=None)
            embed = discord.Embed(
                title="✨ Resurrection Complete!",
                description=f"{member.mention} has been revived by {interaction.user.mention}! Hopefully, they behave this time. 🤞",
                color=discord.Color.green()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308808048030126162/love-live-static.gif?ex=673f49fb&is=673df87b&hm=e53b7c74842f2939f60c71bdad015a1013b28c0476f41244e8a8091464143f02&")
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to revive them. RIP again. 😔", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Failed to revive. The afterlife is holding onto them tight.", ephemeral=True)
        except Exception as e:
            print(f"- [ERROR] {e}")

    @app_commands.command(name="chaos", description="Unleash chaos on the server (temporarily).")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def chaos_cmd(self, interaction: discord.Interaction):
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "chaos"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            members = interaction.guild.members
            skipped_members = []  # Track members that couldn't be edited

            for member in random.sample(members, min(len(members), 10)):
                try:
                    random_nickname = f"💥 {random.choice(['Goblin', 'Legend', 'Potato', 'Dud'])}"
                    await member.edit(nick=random_nickname)
                except discord.Forbidden:
                    skipped_members.append(member)
                except discord.HTTPException:
                    continue  # Ignore and move to the next member

            chaos_message = "Chaos unleashed! Check those nicknames. 😈"
            if skipped_members:
                chaos_message += f"\n\nCouldn't touch {len(skipped_members)} members. They're either protected or untouchable. 😏"

            await interaction.followup.send(chaos_message)

            # Reset the chaos after some time
            await asyncio.sleep(60)
            for member in members:
                try:
                    await member.edit(nick=None)
                except (discord.Forbidden, discord.HTTPException):
                    continue  # Skip members we can't reset

            await interaction.followup.send("Chaos reverted. Everyone's back to normal. For now.")
        except Exception as e:
            print(f"- [ERROR] {e}")
            await interaction.followup.send("Something went wrong during chaos mode. Abort!", ephemeral=True)


    @app_commands.command(name="prank", description="Play a harmless prank on a member!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def prank_cmd(self, interaction: discord.Interaction, member: discord.Member):
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "prank"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
        await interaction.response.defer()
        if member.id == 1230672301364871188:
            prank_nick = f"{member.name} 🤡"
            try:
                await member.edit(nick=prank_nick)
                await interaction.followup.send(f"`{member.mention}` is now known as `{prank_nick}`. Let the giggles begin!")
            except discord.Forbidden:
                await interaction.followup.send("I can't prank them. They're protected by Discord gods. 🙄", ephemeral=True)
            except Exception as e:
                print(f"- [ERROR] {e}")

        else:
            prank_nick = f"{member.name} 🤡"
            try:
                await member.edit(nick=prank_nick)
                await interaction.followup.send(f"`{member.mention}` is now known as `{prank_nick}`. Let the giggles begin!")
                await asyncio.sleep(60)
                await member.edit(nick=None)
                await interaction.followup.send("Prank over. Nickname restored!")
            except discord.Forbidden:
                await interaction.followup.send("I can't prank them. They're protected by Discord gods. 🙄", ephemeral=True)
            except Exception as e:
                print(f"- [ERROR] {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(MISC(bot))