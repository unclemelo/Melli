import discord
from discord.ext import commands, tasks
import datetime
import json
import os

STATS_FILE = "data/bot_stats.json"

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_usage = 0
        self.channel_id = None
        self.message_id = None
        self.bot_version = "v?.?.?"
        self.start_time = datetime.datetime.utcnow()

        self.load_stats()
        self.update_stats.start()

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
                self.command_usage = data.get("command_usage", 0)
                self.channel_id = data.get("stats_channel")
                self.bot_version = data.get("bot_version", "v?.?.?")
                self.message_id = data.get("message_id")
        else:
            self.command_usage = 0
            self.channel_id = None
            self.bot_version = "v?.?.?"
            self.message_id = None

    def save_stats(self):
        with open(STATS_FILE, "w") as f:
            json.dump({
                "command_usage": self.command_usage,
                "stats_channel": self.channel_id,
                "bot_version": self.bot_version,
                "message_id": self.message_id
            }, f, indent=4)

    def cog_unload(self):
        self.update_stats.cancel()
        self.save_stats()

    def get_uptime(self):
        delta = datetime.datetime.utcnow() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        return " ".join(parts)

    @commands.Cog.listener()
    async def on_application_command(self, interaction: discord.Interaction):
        self.command_usage += 1
        self.save_stats()

    @tasks.loop(seconds=60)
    async def update_stats(self):
        guilds = self.bot.guilds
        guild_count = len(guilds)
        member_count = sum(g.member_count or 0 for g in guilds)
        unique_users = {member.id for g in guilds for member in g.members}
        channel_count = sum(len(g.channels) for g in guilds)
        role_count = sum(len(g.roles) for g in guilds)
        avg_ping = round(self.bot.latency * 1000, 2)
        uptime = self.get_uptime()

        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.from_str("#FC6C85"),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Servers", value=str(guild_count), inline=True)
        embed.add_field(name="Members", value=str(member_count), inline=True)
        embed.add_field(name="Unique Users", value=str(len(unique_users)), inline=True)
        embed.add_field(name="Commands Used", value=str(self.command_usage), inline=True)
        embed.add_field(name="Avg Ping", value=f"{avg_ping}ms", inline=True)
        embed.add_field(name="Total Channels", value=str(channel_count), inline=True)
        embed.add_field(name="Total Roles", value=str(role_count), inline=True)
        embed.add_field(name="Uptime", value=uptime, inline=True)
        embed.add_field(name="Version", value=self.bot_version, inline=True)
        embed.set_footer(text="Last updated")

        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        try:
            if self.message_id:
                msg = await channel.fetch_message(self.message_id)
                await msg.edit(embed=embed)
            else:
                msg = await channel.send(embed=embed)
                self.message_id = msg.id
                self.save_stats()
        except discord.NotFound:
            msg = await channel.send(embed=embed)
            self.message_id = msg.id
            self.save_stats()

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(StatsCog(bot))
