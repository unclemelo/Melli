import discord
from discord.ext import commands
import time
from typing import Literal

SUPPORT_SERVER_ID = 1290420853926002789

BUCKET_TYPES = {
    "user": lambda interaction: interaction.user.id,
    "guild": lambda interaction: interaction.guild.id if interaction.guild else interaction.user.id,
}

class BoosterCooldownManager:
    def __init__(self, rate: int, per: float, bucket_type: Literal["user", "guild"] = "user"):
        self.rate = rate
        self.per = per
        self.bucket_type = bucket_type
        self.cooldowns = {}  # key -> [timestamps]

    def _get_key(self, interaction: discord.Interaction):
        return BUCKET_TYPES[self.bucket_type](interaction)

    async def get_remaining(self, interaction: discord.Interaction) -> float:
        key = self._get_key(interaction)
        now = time.time()

        # Get member for booster check
        guild = interaction.client.get_guild(SUPPORT_SERVER_ID)
        member = guild.get_member(interaction.user.id) if guild else None
        cooldown_period = self.per * 0.7 if member and member.premium_since else self.per

        timestamps = self.cooldowns.get(key, [])
        # Filter timestamps still within cooldown period
        valid = [t for t in timestamps if now - t < cooldown_period]
        self.cooldowns[key] = valid

        if len(valid) >= self.rate:
            return cooldown_period - (now - valid[0])
        else:
            return 0.0

    async def trigger(self, interaction: discord.Interaction):
        key = self._get_key(interaction)
        now = time.time()
        self.cooldowns.setdefault(key, []).append(now)
