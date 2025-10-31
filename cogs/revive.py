import discord, random, json, os
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from util.command_checks import command_enabled
from util.booster_cooldown import BoosterCooldownManager

cooldown_manager_user = BoosterCooldownManager(rate=1, per=600, bucket_type="user")
STATS_FILE = "data/royal_stats.json"

class Revive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.stats = self.load_stats()

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

    def xp_needed(self, level: int):
        return 100 + (level * 25)

    def add_xp(self, user_id: str, amount: int):
        user = self.get_user(user_id)
        user["xp"] += amount
        leveled_up = False
        while user["xp"] >= self.xp_needed(user["level"]):
            user["xp"] -= self.xp_needed(user["level"])
            user["level"] += 1
            if user["level"] > 50:
                user["level"] = 50
            leveled_up = True
        self.save_stats()
        return leveled_up

    def add_revive(self, user_id: str, success: bool):
        user = self.get_user(user_id)
        if success:
            user["revives"] += 1
            # Gain XP for successful revive
            xp_gain = random.randint(15, 30)
            leveled_up = self.add_xp(user_id, xp_gain)
            return xp_gain, leveled_up
        else:
            user["failed_revives"] += 1
            self.save_stats()
            return 0, False

    @app_commands.command(name="revive", description="Attempt to bring a timed-out user back to life!")
    @command_enabled()
    async def revivecmd(self, interaction: discord.Interaction, member: discord.Member):
        remaining = await cooldown_manager_user.get_remaining(interaction)
        if remaining > 0:
            await interaction.response.send_message(
                f"⏳ Your healing hands need to rest! Try again in **{round(remaining, 1)}s.**",
                ephemeral=True
            )
            return

        await cooldown_manager_user.trigger(interaction)

        if member == interaction.user:
            await interaction.response.send_message(
                "🪞 You can't revive yourself — the dead can't heal the dead!", ephemeral=True
            )
            return

        # Determine outcome (higher fail rate)
        outcome = random.choices(["fail", "success", "miracle"], weights=[0.3, 0.6, 0.1])[0]

        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_footer(text="🕐 Cooldown: 10 minutes")

        if outcome == "fail":
            embed.title = "💀 Revival Failed!"
            embed.description = f"{interaction.user.mention} tried to revive {member.mention}, but the light **flickered and went out.**\n" \
                                 f"The afterlife wasn’t ready to let go just yet..."
            embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1326217477395953726/revive-fail.gif")
            self.add_revive(interaction.user.id, success=False)

        elif outcome == "miracle":
            embed.title = "🌈 Miracle Revival!"
            embed.description = f"✨ Against all odds, {interaction.user.mention} performed a **miracle revival!**\n" \
                                 f"{member.mention} rises again with divine energy!"
            embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308808048030126162/love-live-static.gif")
            try:
                await member.edit(timed_out_until=None)
                xp_gain, leveled_up = self.add_revive(interaction.user.id, success=True)
                if xp_gain > 0:
                    embed.add_field(name="XP Gained", value=f"✨ {xp_gain} XP")
                if leveled_up:
                    embed.add_field(name="Level Up!", value=f"📈 You leveled up!")
            except discord.Forbidden:
                embed.description += "\n⚠️ But the spell fizzled... I lacked the power to complete it."
                self.add_revive(interaction.user.id, success=False)

        else:  # normal success
            embed.title = "✨ Resurrection Complete!"
            embed.description = f"{interaction.user.mention} has successfully revived {member.mention}! 🙌\n" \
                                 f"Let’s hope they behave this time..."
            embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308808048030126162/love-live-static.gif")
            try:
                await member.edit(timed_out_until=None)
                xp_gain, leveled_up = self.add_revive(interaction.user.id, success=True)
                if xp_gain > 0:
                    embed.add_field(name="XP Gained", value=f"✨ {xp_gain} XP")
                if leveled_up:
                    embed.add_field(name="Level Up!", value=f"📈 You leveled up!")
            except discord.Forbidden:
                embed.description = "😔 The ritual failed... I don’t have permission to revive them."
                self.add_revive(interaction.user.id, success=False)
            except discord.HTTPException:
                embed.description = "👻 Something went wrong during revival — maybe next time."
                self.add_revive(interaction.user.id, success=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Revive(bot))
