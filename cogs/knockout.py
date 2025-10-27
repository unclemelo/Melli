import discord, random, asyncio, json, os
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from util.command_checks import command_enabled
from util.booster_cooldown import BoosterCooldownManager

cooldown_manager_user = BoosterCooldownManager(rate=1, per=600, bucket_type="user")

STATS_FILE = "data/royal_stats.json"
WEAPON_FILE = "data/weapons.json"


class Royal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.stats = self.load_stats()
        self.weapons = self.load_weapons()

    # === Stats handling ===
    def load_stats(self):
        if not os.path.exists(STATS_FILE):
            os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
            with open(STATS_FILE, "w") as f:
                json.dump({}, f)
        with open(STATS_FILE, "r") as f:
            return json.load(f)

    def save_stats(self):
        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f, indent=4)

    def get_user(self, user_id: str):
        if str(user_id) not in self.stats:
            self.stats[str(user_id)] = {
                "kills": 0, "deaths": 0,
                "revives": 0, "failed_revives": 0,
                "xp": 0, "level": 1, "prestige": 0
            }
        return self.stats[str(user_id)]

    def add_kill(self, user_id: str):
        user = self.get_user(user_id)
        user["kills"] += 1
        self.save_stats()

    def add_death(self, user_id: str):
        user = self.get_user(user_id)
        user["deaths"] += 1
        self.save_stats()

    def add_xp(self, user_id: str, amount: int):
        user = self.get_user(user_id)
        user["xp"] += amount
        leveled_up = False
        while user["xp"] >= 100 + (user["level"] * 25):
            user["xp"] -= 100 + (user["level"] * 25)
            user["level"] += 1
            leveled_up = True
        self.save_stats()
        return leveled_up

    # === Weapons handling ===
    def load_weapons(self):
        if not os.path.exists(WEAPON_FILE):
            raise FileNotFoundError(f"Weapon file missing: {WEAPON_FILE}")
        with open(WEAPON_FILE, "r") as f:
            return json.load(f)

    # === Main command ===
    @app_commands.command(name="knockout", description="Knock someone out with a random weapon!")
    @command_enabled()
    async def knockoutcmd(self, interaction: discord.Interaction, member: discord.Member = None):
        remaining = await cooldown_manager_user.get_remaining(interaction)
        if remaining > 0:
            await interaction.response.send_message(
                f"⏳ Whoa there, hotshot! You need to reload — try again in **{round(remaining, 1)}s.**",
                ephemeral=True
            )
            return

        await cooldown_manager_user.trigger(interaction)

        if member is None:
            member = random.choice([m for m in interaction.guild.members if not m.bot])

        if member == interaction.guild.me:
            await interaction.response.send_message("❌ I'm not going down that easily!", ephemeral=True)
            return
        elif member == interaction.user:
            embed = discord.Embed(
                title="Need Help?",
                description="It's okay to reach out — you matter ❤️\n`988` Suicide and Crisis Lifeline",
                color=discord.Color.red()
            )
            embed.set_footer(text="Available 24/7 — English & Spanish")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # === Load and choose weapon ===
        weapons = self.weapons
        weapon_key = random.choice(list(weapons.keys()))
        weapon = weapons[weapon_key]
        timeout_value = random.choice(weapon["timeout"]) if isinstance(weapon["timeout"], list) else weapon["timeout"]

        outcome = random.choices(["hit", "miss", "crit"], weights=[0.75, 0.15, 0.10])[0]
        embed = discord.Embed(color=discord.Color.magenta(), title=weapon["title"])
        embed.set_image(url=weapon["gif"])

        if outcome == "miss":
            embed.description = f"😅 {interaction.user.mention} tried to hit {member.mention} with a random weapon but **missed!**"
        elif outcome == "crit":
            crit_time = timeout_value * 2
            await member.timeout(discord.utils.utcnow() + timedelta(seconds=crit_time), reason="Critical hit!")
            embed.description = f"🔥 **CRITICAL HIT!** {interaction.user.mention} annihilated {member.mention} with a {weapon_key}! They're out cold for **{crit_time}s!**"
            self.add_kill(interaction.user.id)
            self.add_death(member.id)
            self.add_xp(interaction.user.id, random.randint(15, 30))
        else:
            await member.timeout(discord.utils.utcnow() + timedelta(seconds=timeout_value), reason="Knocked out!")
            embed.description = f"{interaction.user.mention} used a **{weapon_key}** on {member.mention}! {random.choice(weapon['lines'])}"
            self.add_kill(interaction.user.id)
            self.add_death(member.id)
            self.add_xp(interaction.user.id, random.randint(10, 25))

        embed.set_footer(text="🕐 Cooldown: 10 minutes")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Royal(bot))
