import discord
import json
from discord import app_commands
from discord.ext import commands

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Moderation", custom_id="help_moderation", style=discord.ButtonStyle.primary))
        self.add_item(discord.ui.Button(label="Fun", custom_id="help_fun", style=discord.ButtonStyle.secondary))
        self.add_item(discord.ui.Button(label="Utility", custom_id="help_utility", style=discord.ButtonStyle.success))

# Load commands from JSON file
with open("data/commands.json", "r") as file:
    command_categories = json.load(file)

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get a list of available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Help Menu", description="Click a button below to view commands in each category.", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            category = interaction.data["custom_id"].split("_")[1].capitalize()
            if category in command_categories:
                embed = discord.Embed(title=f"{category} Commands", description="\n".join(command_categories[category]), color=discord.Color.blurple())
                await interaction.response.edit_message(embed=embed, view=HelpView())

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
