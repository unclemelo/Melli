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
from util.command_checks import command_enabled
from util.booster_cooldown import BoosterCooldownManager

cooldown_manager_user = BoosterCooldownManager(rate=1, per=600, bucket_type="user")
cooldown_manager_guild = BoosterCooldownManager(rate=1, per=600, bucket_type="guild")


class MISC(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="chaos", description="Unleash chaos on the server (temporarily).")
    @command_enabled()
    async def chaos_cmd(self, interaction: discord.Interaction):
        remaining = await cooldown_manager_user.get_remaining(interaction)
        if remaining > 0:
            await interaction.response.send_message(
                f"You're on cooldown! Try again in {round(remaining, 1)}s.", ephemeral=True
            )
            return

        await cooldown_manager_user.trigger(interaction)

        
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
    @command_enabled()
    async def prank_cmd(self, interaction: discord.Interaction, member: discord.Member):
        remaining = await cooldown_manager_user.get_remaining(interaction)
        if remaining > 0:
            await interaction.response.send_message(
                f"You're on cooldown! Try again in {round(remaining, 1)}s.", ephemeral=True
            )
            return

        await cooldown_manager_user.trigger(interaction)
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