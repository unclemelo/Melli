import discord
from discord import app_commands
from discord.ext import commands

class AddMelli(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add_melli", description="Get an invite link to add Melli to your server.")
    async def add_melli(self, interaction: discord.Interaction):
        invite_url = "https://discord.com/oauth2/authorize?client_id=1316235145778434070&permissions=8&integration_type=0&scope=bot"
        view = discord.ui.View()
        button = discord.ui.Button(label="Add Melli", url=invite_url, style=discord.ButtonStyle.link)
        view.add_item(button)
        
        await interaction.response.send_message("Click the button below to invite Melli to your server!", view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AddMelli(bot))

