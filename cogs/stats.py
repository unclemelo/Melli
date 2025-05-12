import discord
from discord.ext import commands, tasks
import datetime

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_usage = 0
        self.channel_id = 1371140885609451651
        self.message_id = None
        self.start_time = datetime.datetime.utcnow()
        self.bot_version = "v1.20.7"  # Change as needed
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @commands.Cog.listener()
    async def on_application_command(self, interaction: discord.Interaction):
        self.command_usage += 1

    @tasks.loop(seconds=60)
    async def update_stats(self):
        guilds = self.bot.guilds
        guild_count = len(guilds)
        member_count = sum(g.member_count or 0 for g in guilds)

        # Unique user IDs across all guilds
        unique_users = {member.id for g in guilds for member in g.members}
        channel_count = sum(len(g.channels) for g in guilds)
        role_count = sum(len(g.roles) for g in guilds)

        avg_ping = round(self.bot.latency * 1000, 2)
        uptime = discord.utils.format_dt(self.start_time, style="R")

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
        except discord.NotFound:
            msg = await channel.send(embed=embed)
            self.message_id = msg.id

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(StatsCog(bot))
