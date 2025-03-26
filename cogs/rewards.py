import discord
from discord import app_commands
from discord.ext import commands
import json
import datetime

class Whois(commands.Cog):
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
            if user_id not in self.data:
                self.data[user_id] = {"command_count": 1, "first_use": datetime.datetime.utcnow().isoformat()}
            else:
                self.data[user_id]["command_count"] = self.data[user_id].get("command_count", 0) + 1
            
            self.save_data()
        except Exception as e:
            print(f"Error updating command count: {e}")
    
    def get_badges(self, command_count, first_use):
        try:
            badges = []
            first_use_date = datetime.datetime.fromisoformat(first_use)
            days_using = (datetime.datetime.utcnow() - first_use_date).days
            
            if command_count >= 100:
                badges.append("🥉")
            if command_count >= 500:
                badges.append("🥈")
            if command_count >= 1000:
                badges.append("🥇")
            
            if days_using >= 30:
                badges.append("📅")
            if days_using >= 180:
                badges.append("🎖️")
            if days_using >= 365:
                badges.append("🏆")
            
            return badges
        except Exception as e:
            print(f"Error calculating badges: {e}")
            return []
    
    def get_level(self, command_count):
        try:
            return command_count // 100  # 1 level per 100 commands
        except Exception as e:
            print(f"Error calculating level: {e}")
            return 0

    @app_commands.command(name="profile", description="View the profile we gave you on the bot.")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        try:
            member = member or interaction.user
            user_id = str(member.id)
            if user_id not in self.data:
                await interaction.response.send_message(f"{member.display_name} has not used the bot yet.")
                return
            
            command_count = self.data[user_id].get("command_count", 0)
            first_use = self.data[user_id].get("first_use", datetime.datetime.utcnow().isoformat())
            badges = self.get_badges(command_count, first_use)
            level = self.get_level(command_count)
            
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
    await bot.add_cog(Whois(bot))
