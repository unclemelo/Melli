import discord, json, os, random
from discord.ext import commands
from discord import app_commands

DATA_FILE = "data/royal_stats.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


class PrestigeButton(discord.ui.View):
    def __init__(self, user_id: int, cog, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.cog = cog

    @discord.ui.button(label="Prestige Now ⭐", style=discord.ButtonStyle.primary, emoji="✨")
    async def prestige_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn’t your prestige menu!", ephemeral=True)
            return

        user = self.cog.get_user(self.user_id)
        if user["level"] < self.cog.max_level:
            await interaction.response.send_message("You haven’t reached max level yet!", ephemeral=True)
            return

        # Confirm prestige
        user["prestige"] += 1
        user["level"] = 1
        user["xp"] = 0
        save_data(self.cog.data)

        stars = "★" * user["prestige"]
        embed = discord.Embed(
            title="🌟 Prestige Achieved!",
            description=f"{interaction.user.mention} has ascended to **Prestige {user['prestige']}!**\n\n"
                        f"{stars}\n\nYour level and XP have been reset.",
            color=discord.Color.gold()
        )
        await interaction.response.edit_message(embed=embed, view=None)


class RoyalStats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = load_data()
        self.max_level = 50

    # --- Helpers ---
    def get_user(self, user_id: int):
        uid = str(user_id)
        if uid not in self.data:
            self.data[uid] = {
                "kills": 0,
                "deaths": 0,
                "revives": 0,
                "xp": 0,
                "level": 1,
                "prestige": 0
            }
        return self.data[uid]

    def add_xp(self, user_id: int, amount: int):
        user = self.get_user(user_id)
        user["xp"] += amount
        msg = None

        while user["xp"] >= self.xp_needed(user["level"]):
            user["xp"] -= self.xp_needed(user["level"])
            user["level"] += 1
            if user["level"] >= self.max_level:
                user["level"] = self.max_level
                msg = f"🌟 You’ve reached **Level {self.max_level}!** Ready to Prestige!"
                break
            else:
                msg = f"⬆️ Leveled up to **Level {user['level']}!**"

        save_data(self.data)
        return msg

    def xp_needed(self, level: int):
        return 100 + (level * 25)

    # --- Commands ---
    @app_commands.command(name="royalstats", description="Check your Royal stats and prestige progress.")
    async def royalstats(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = self.get_user(member.id)

        kills, deaths, revives = user["kills"], user["deaths"], user["revives"]
        xp, level, prestige = user["xp"], user["level"], user["prestige"]
        kd_ratio = round(kills / deaths, 2) if deaths > 0 else kills
        prestige_stars = "★" * prestige

        embed = discord.Embed(
            title=f"🏆 Royal Stats — {member.display_name} {prestige_stars}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Kills", value=f"🔪 {kills}", inline=True)
        embed.add_field(name="Deaths", value=f"💀 {deaths}", inline=True)
        embed.add_field(name="Revives", value=f"❤️ {revives}", inline=True)
        embed.add_field(name="K/D Ratio", value=f"⚔️ {kd_ratio}", inline=True)
        embed.add_field(name="Level", value=f"📈 {level}", inline=True)
        embed.add_field(name="XP", value=f"✨ {xp}/{self.xp_needed(level)}", inline=True)
        embed.add_field(name="Prestige", value=f"{prestige_stars or '—'}", inline=False)

        # Only show Prestige button if available
        view = None
        if member.id == interaction.user.id and level >= self.max_level:
            view = PrestigeButton(member.id, self)


        # ✅ Safely send message
        if view:
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed)



async def setup(bot: commands.Bot):
    await bot.add_cog(RoyalStats(bot))
