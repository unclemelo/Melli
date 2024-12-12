import discord, json
from discord.ext import commands
from datetime import timedelta
from discord import app_commands
from colorama import Fore

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_file = "data/AM_regex.json"
        self.load_config()


    def load_config(self):
        """Load the configuration from the JSON file."""
        try:
            with open(self.config_file, "r") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = {
                "blocked_links_regex": [],
                "allowed_links": []
            }

    @app_commands.command(name="allowed_links", description="Displays the list of all allowed links.")
    async def allowedlinks(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Allowed Links",
            description="Here are the links allowed in this server:",
            color=0x3df553  # Use a consistent theme color for your bot
        )

        # Check if the allowed_links list is empty
        allowed_links = self.config.get("allowed_links", [])

        # If there are allowed links, format them with bullets; otherwise, display a fallback message
        if allowed_links:
            allowed = "\n• ".join(allowed_links)  # Join allowed links with a bullet
        else:
            allowed = "No allowed links."  # If empty, show this message
        
        # Add the formatted allowed links to the embed
        embed.add_field(
            name="🔗 Links",
            value=f"• `{allowed}`",  # Display the links with a bullet if there are any
            inline=False
        )
        
        # Set the footer with guild icon if available
        embed.set_footer(
            text="Please contact your server admin for the list of links.", 
            icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None
        )

        # Send the embed message
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
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None) #temp until we get out logo
        embed.set_footer(text="We're here to help! 🍉")

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="m", description="Melo's socials.")
    async def m_social(self, interaction: discord.Interaction):
        bsky_link = "https://bsky.app/profile/unclemelo.bsky.social"
        twitch_link = "https://www.twitch.tv/uncle_melo_"
        yt_link = "https://www.youtube.com/@unclemelo"
        tiktok_link = "https://www.tiktok.com/@uncle_melo_"
        github_link = "https://github.com/unclemelo"
        discord_link = "https://discord.gg/bsWukZXg8s"

        embed = discord.Embed(
            title="Uncle Melo's Socials",
            description="Check out Uncle Melo on various platforms!",
            color=discord.Color.blue()
        )
        embed.add_field(name="<:bluesky:1313595815884755035> BlueSky", value=f"[Click here]({bsky_link})", inline=False)
        embed.add_field(name="<:twitch:1313592912965144576> Twitch", value=f"[Click here]({twitch_link})", inline=False)
        embed.add_field(name="<:youtube:1313592929259884716> YouTube", value=f"[Click here]({yt_link})", inline=False)
        embed.add_field(name="<:tiktok:1313592945735368847> TikTok", value=f"[Click here]({tiktok_link})", inline=False)
        embed.add_field(name="<:blurplegithub:1313592960385941504> GitHub", value=f"[Click here]({github_link})", inline=False)
        embed.add_field(name="<:discord:1313592889418317867> Discord Server", value=f"[Click here]({discord_link})", inline=False)
        embed.set_footer(text="Follow Melo on all platforms!")

        await interaction.response.send_message(embed=embed)





async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))
