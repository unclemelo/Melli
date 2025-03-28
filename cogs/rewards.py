import discord
from discord import app_commands
from discord.ext import commands
import json
import datetime
from util.command_checks import is_command_enabled

class Rewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = "data/user_stats.json"
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.file, "r") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}
    
    def save_data(self):
        try:
            with open(self.file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try:
            if interaction.command is None:
                return  # Ignore non-command interactions
            
            user_id = str(interaction.user.id)
            user = interaction.user
            first_use = False  # Track if it's the user's first time using the bot

            if user_id not in self.data:
                self.data[user_id] = {
                    "command_count": 1,
                    "first_use": datetime.datetime.utcnow().isoformat(),
                    "badges": ["🎉"]  # First-time user badge
                }
                first_use = True  # This is the user's first time using the bot
            else:
                self.data[user_id]["command_count"] += 1

                # Ensure badges exist
                if "badges" not in self.data[user_id]:
                    self.data[user_id]["badges"] = []

                # Add the 🎉 badge if the user is new
                if first_use and "🎉" not in self.data[user_id]["badges"]:
                    self.data[user_id]["badges"].append("🎉")

                # Update other badges based on milestones
                self.update_badges(user_id)

            prev_level = self.get_level(self.data[user_id]["command_count"] - 1)
            new_level = self.get_level(self.data[user_id]["command_count"])
            
            self.save_data()

            # Announce first-time usage and reward badge
            if first_use:
                await self.announce_reward(interaction.channel, user, "🎉 First-time User! You've earned your first badge!")

            # Announce level-up
            if new_level > prev_level:
                await self.announce_reward(interaction.channel, user, f"🎉 {user.mention} has leveled up to Level {new_level}! Keep it up! 🚀")

        except Exception as e:
            print(f"Error updating command count: {e}")

    async def announce_reward(self, channel, user, message):
        """Send an announcement message in the same channel where the command was used."""
        if channel:
            embed = discord.Embed(title="🏆 Achievement Unlocked!", description=message, color=discord.Color.gold())
            embed.set_thumbnail(url=user.avatar.url)
            await channel.send(embed=embed)

    def update_badges(self, user_id):
        """Check and update user badges based on their command count and bot usage time."""
        try:
            user_data = self.data.get(user_id, {})
            command_count = user_data.get("command_count", 0)
            first_use_date = datetime.datetime.fromisoformat(user_data.get("first_use", datetime.datetime.utcnow().isoformat()))
            days_using = (datetime.datetime.utcnow() - first_use_date).days

            badges = set(user_data.get("badges", []))  # Convert to a set to avoid duplicates

            # Command count badges
            if command_count >= 100:
                badges.add("🥉")  # Bronze
            if command_count >= 500:
                badges.add("🥈")  # Silver
            if command_count >= 1000:
                badges.add("🥇")  # Gold

            # Time-based badges
            if days_using >= 30:
                badges.add("📅")  # One month user
            if days_using >= 180:
                badges.add("🎖️")  # Six months user
            if days_using >= 365:
                badges.add("🏆")  # One year user

            # Update user data
            self.data[user_id]["badges"] = list(badges)

        except Exception as e:
            print(f"Error updating badges: {e}")

    def get_level(self, command_count):
        try:
            return command_count // 100  # 1 level per 100 commands
        except Exception as e:
            print(f"Error calculating level: {e}")
            return 0

    @app_commands.command(name="profile", description="View the profile we gave you on the bot.")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        # ✅ Check if the command is enabled before executing, using the function itself
        if not is_command_enabled(interaction.guild.id, "profile"):
            await interaction.response.send_message("🚫 This command is disabled in this server.", ephemeral=True)
            return
        try:
            member = member or interaction.user
            user_id = str(member.id)
            if user_id not in self.data:
                await interaction.response.send_message(f"{member.display_name} has not used the bot yet.")
                return
            
            command_count = self.data[user_id].get("command_count", 0)
            level = self.get_level(command_count)
            badges = self.data[user_id].get("badges", [])

            embed = discord.Embed(title=f"{member.display_name}'s Profile", color=discord.Color.blue())
            embed.add_field(name="Commands Used", value=str(command_count), inline=False)
            embed.add_field(name="Level", value=f"{level}", inline=False)
            embed.add_field(name="Badges", value=" ".join(badges) if badges else "None", inline=False)
            embed.set_thumbnail(url=member.avatar.url)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error displaying profile: {e}")
            await interaction.response.send_message("An error occurred while retrieving the profile.")

async def setup(bot):
    await bot.add_cog(Rewards(bot))
