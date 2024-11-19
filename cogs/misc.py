import discord
from discord.ext import commands
from datetime import timedelta
from discord import app_commands
from colorama import Fore

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded misc.py")

    @app_commands.command(name="allowed_links", description="Displays the list of all allowed links.")
    async def allowedlinks(self, interaction: discord.Interaction):
        allowed_links = [
            "https://c.tenor.com/",
            "https://cdn.discordapp.com/",
            "https://imgflip.com/",
            "https://media.discordapp.net/",
            "https://on.soundcloud.com/",
            "https://open.spotify.com/",
            "https://tenor.com/",
            "https://www.bilibili.com/",
            "https://www.youtube.com/",
            "https://youtu.be/",
            "https://youtube.com/"
        ]

        embed = discord.Embed(
            title="Allowed Links",
            description="Here are the links allowed in this server:",
            color=0x3df553  # Use a consistent theme color for your bot
        )
        embed.add_field(
            name="🔗 Links",
            value="\n".join(f"• {link}" for link in allowed_links),
            inline=False
        )
        embed.set_footer(text="Please ensure your links adhere to these guidelines.", icon_url=interaction.guild.icon.url if interaction.guild else None)

        await interaction.response.send_message(embed=embed)

    
    @app_commands.command(name="support_server", description="Get the invite link to the bot's support server.")
    async def support_server(self, interaction: discord.Interaction):
        # Replace this URL with your actual support server invite link
        support_server_link = "https://discord.gg/FgD5jdf8yA"

        embed = discord.Embed(
            title="Join the Support Server!",
            description=(
                "Need help with the bot or want to suggest new features?\n"
                "Click the link below to join our support server!"
            ),
            color=0x7289DA  # Discord-themed blue color
        )
        embed.add_field(
            name="🔗 Support Server Link",
            value=f"[Click here to join]({support_server_link})",
            inline=False
        )
        embed.set_thumbnail(url="https://example.com/logo.png")  # Replace with your bot/server logo URL
        embed.set_footer(text="We're here to help! 🍉")

        await interaction.response.send_message(embed=embed)





async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))
