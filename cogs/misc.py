import discord
import asyncio
import random
import json
import os
from discord.ext import commands
from discord import app_commands
from colorama import Fore
from typing import List
from discord.ext.commands import cooldown, BucketType
from datetime import timedelta

BUMP_DATA_FILE = "data/bump_data.json"

class MISC(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if os.path.exists(BUMP_DATA_FILE):
            with open(BUMP_DATA_FILE, "r") as file:
                self.bump_data = json.load(file)
        else:
            self.bump_data = {}
        self.bump_reminders = {}
        self.reminder_task.start()

    @app_commands.command(name="bump", description="bro why are you bumping???")
    @app_commands.checks.cooldown(1, 7200, key=lambda i: (i.guild.id))
    async def bumpcmd(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        if guild_id not in self.bump_data:
            self.bump_data[guild_id] = {}

        if user_id not in self.bump_data[guild_id]:
            self.bump_data[guild_id][user_id] = 0
        self.bump_data[guild_id][user_id] += 1

        self.save_bump_data()

        embed = discord.Embed(
            title="Bump Command Usage",
            description=f"{interaction.user.mention}, you have used the `bump` command {self.bump_data[guild_id][user_id]} time(s)!",
            color=discord.Color.green()
        )
        embed.add_field(name="Cooldown", value="You can use this command again in 2 hours.", inline=False)

        await interaction.response.send_message(embed=embed)

        # Schedule a reminder
        if (guild_id) not in self.bump_reminders:
            self.bump_reminders[(guild_id)] = asyncio.create_task(self.send_bump_reminder(interaction))

    async def send_bump_reminder(self, interaction):
        await asyncio.sleep(7200)  # Wait for 2 hours

        try:
            await interaction.followup.send(f"<@&1313894996637650985>, You can bump again dummies.")
        except discord.HTTPException:
            pass  # Handle any errors silently

        # Remove reminder tracking
        guild_id = str(interaction.guild.id)
        self.bump_reminders.pop((guild_id), None)

    @tasks.loop(hours=1)
    async def reminder_task(self):
        """ Cleans up finished reminders to prevent memory leaks. """
        self.bump_reminders = {k: v for k, v in self.bump_reminders.items() if not v.done()}

    @app_commands.command(name="help", description="Shows the list of commands categorized")
    async def helpcmd(self, interaction: discord.Interaction):
        """Displays an interactive help menu with categorized commands."""

        try:
            # Define command categories
            command_categories = {
                "Moderation": ["</ban:1330966727948894299>", "</kick:1330966727948894300>", "</mute:1331002213983846452>", "</unmute:1331002213983846453>", "</warn:1330897980462600299>", "</warnings:1330897980462600300>", "</clear:1331002213983846454>", "</clearwarns:1330897980945076267>", "</delwarn:1330897980945076266>", "</unban:1331002213983846450>"],
                "Fun": ["</chaos:1326163954531176572>", "</cheese:1331705714950803496>", "</knockout:1326163954531176570>", "</prank:1326163954531176573>", "</revive:1326163954531176571>", "</votekick:1328523711216881716>", "</credits:1331872616163704874>"],
                "Utility": ["</automod_setup:1334418507219210241>", "</uptime:1321819862628302920>", "</reboot:1316240452038561814> - **Dev Only**", "</shutdown:1321819862628302919> - **Dev Only**"]
            }

            # Build the embeds
            embeds = []
            for category, commands in command_categories.items():
                embed = discord.Embed(
                    title=f"Help: {category}",
                    description="\n".join(commands),
                    color=0x3474eb
                )
                embed.set_footer(text="Use the buttons below to navigate.")
                embeds.append(embed)

            # Button navigation
            class HelpView(discord.ui.View):
                def __init__(self, embeds: List[discord.Embed]):
                    super().__init__(timeout=60)
                    self.embeds = embeds
                    self.current_page = 0

                async def update_embed(self, interaction: discord.Interaction):
                    await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

                @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
                async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = (self.current_page - 1) % len(self.embeds)
                    await self.update_embed(interaction)

                @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
                async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = (self.current_page + 1) % len(self.embeds)
                    await self.update_embed(interaction)

            # Send the first embed with the interactive view
            await interaction.response.send_message(embed=embeds[0], view=HelpView(embeds), ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while generating the help menu. Please contact an administrator.\n```{e}```",
                ephemeral=True
            )

    @app_commands.command(name="cheese", description="cheese")
    async def cheesecmd(self, interaction: discord.Interaction):
        try:            
            embed = discord.Embed(title="Cheese", description="Cheese")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1330523346890395764/1331709220785229994/cheese.gif?ex=67929a5c&is=679148dc&hm=3362790ed38cab48622004e784c336fafea720fe0dd2672795ce29a2dbce47f9&")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred. Please contact an administrator.\n```{e}```", ephemeral=True)

    @app_commands.command(name="credits", description="Meet the dev team.")
    async def creditscmd(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title="✨ Credits ✨",
                description="A heartfelt thank you to everyone who contributed to Melli!",
                color=0x5865F2  # A Discord blue shade
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1308048258337345609/1331874809352556597/f0a534c6da023d46a18674bcf5a6a147.png")
            embed.add_field(
                name="👨‍💻 Developers", 
                value="> `@_uncle_melo_`, `@pitr1010`, `@illtana`", 
                inline=False
            )
            embed.add_field(
                name="✍️ Editor", 
                value="> `@mizuki_mochizuki2090`", 
                inline=False
            )
            embed.add_field(
                name="🎨 Artists", 
                value="> `@soupinascoop`, `@bunnnl`", 
                inline=False
            )
            embed.set_footer(
                text="Thanks for supporting Melli!",
                icon_url="https://cdn.discordapp.com/emojis/1323527766011809873.webp"
            )

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred. Please contact an administrator.\n```{e}```", 
                ephemeral=True
            )

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

    
    @app_commands.command(name="revive", description="Bring back a timed-out user with flair!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def revive_cmd(self, interaction: discord.Interaction, member: discord.Member):
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
            print(f"Error: {e}")


    @app_commands.command(name="chaos", description="Unleash chaos on the server (temporarily).")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def chaos_cmd(self, interaction: discord.Interaction):
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
            print(f"Unexpected error: {e}")
            await interaction.followup.send("Something went wrong during chaos mode. Abort!", ephemeral=True)


    @app_commands.command(name="prank", description="Play a harmless prank on a member!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def prank_cmd(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        if member.id == 1230672301364871188:
            prank_nick = f"{member.mention} 🤡"
            try:
                await member.edit(nick=prank_nick)
                await interaction.followup.send(f"`{member.mention}` is now known as `{prank_nick}`. Let the giggles begin!")
            except discord.Forbidden:
                await interaction.followup.send("I can't prank them. They're protected by Discord gods. 🙄", ephemeral=True)
            except Exception as e:
                print(f"Error: {e}")

        else:
            prank_nick = f"{member.mention} 🤡"
            try:
                await member.edit(nick=prank_nick)
                await interaction.followup.send(f"`{member.mention}` is now known as `{prank_nick}`. Let the giggles begin!")
                await asyncio.sleep(60)
                await member.edit(nick=None)
                await interaction.followup.send("Prank over. Nickname restored!")
            except discord.Forbidden:
                await interaction.followup.send("I can't prank them. They're protected by Discord gods. 🙄", ephemeral=True)
            except Exception as e:
                print(f"Error: {e}")

    @app_commands.command(name="uptime", description="Displays the bot's uptime.")
    async def uptime_cmd(self, interaction: discord.Interaction):
        """
        Command to display the bot's uptime.
        """
        uptime = self.get_uptime()
        embed = discord.Embed(
            title="Bot Uptime",
            description=f"`Melli` has been online for: **{uptime}**",
            color=0x3474eb
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(MISC(bot))