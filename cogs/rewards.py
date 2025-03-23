import discord
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
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=4)
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.data:
            self.data[user_id] = {"command_count": 1, "first_use": datetime.datetime.utcnow().isoformat()}
        else:
            self.data[user_id]["command_count"] += 1
        
        self.save_data()
    
    def get_badges(self, command_count, first_use):
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
    
    def get_level(self, command_count):
        return command_count // 100  # 1 level per 100 commands

    @commands.command()
    async def whois(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)
        if user_id not in self.data:
            await ctx.send(f"{member.display_name} has not used the bot yet.")
            return
        
        command_count = self.data[user_id]["command_count"]
        first_use = self.data[user_id]["first_use"]
        badges = self.get_badges(command_count, first_use)
        level = self.get_level(command_count)
        
        embed = discord.Embed(title=f"Whois: {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="Commands Used", value=str(command_count), inline=False)
        embed.add_field(name="Level", value=f"{level}", inline=False)
        embed.add_field(name="Badges", value=" ".join(badges) if badges else "None", inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Whois(bot))
