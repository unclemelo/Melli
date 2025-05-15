import discord
from discord.ext import commands
from discord import app_commands
from util.command_checks import command_enabled

SUPPORT_GUILD_ID = 1290420853926002789
BANNER_URL = "https://cdn.discordapp.com/attachments/1335051139183415306/1371655184849305670/image-removebg-preview.png?ex=6823ecf0&is=68229b70&hm=b68c7f47378124e4932d22d4bd89050f17aefb01ace49cf457b8d26a1c2c2102&"  # Optional banner image

class SupporterLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="supporters", description="Show the top boosters of our support server!")
    @command_enabled()
    async def supporters(self, interaction: discord.Interaction):
        await interaction.response.defer()

        support_guild = self.bot.get_guild(SUPPORT_GUILD_ID)
        if support_guild is None:
            return await interaction.followup.send("Support server not found in cache. Please try again later.", ephemeral=True)

        await support_guild.chunk()

        boosters = [
            member for member in support_guild.members
            if member.premium_since is not None
        ]

        if not boosters:
            return await interaction.followup.send("No boosters found for our support server!", ephemeral=True)

        boosters.sort(key=lambda m: m.premium_since)

        rank_emojis = ["🥇", "🥈", "🥉"]
        leaderboard = ""

        for i, member in enumerate(boosters, start=1):
            emoji = rank_emojis[i - 1] if i <= 3 else "💎"
            boost_date = member.premium_since.strftime("%b %d, %Y")
            leaderboard += f"{emoji} **{i}.** {member.mention} — Boosting since *{boost_date}*\n"

        embed = discord.Embed(
            title="💖 Support Server Boosters",
            description=leaderboard,
            color=discord.Color.magenta()
        )

        embed.set_footer(text="Your support keeps us going! Thank you 💕")
        embed.set_thumbnail(url=support_guild.icon.url if support_guild.icon else discord.Embed.Empty)
        embed.set_image(url=BANNER_URL)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SupporterLeaderboard(bot))
