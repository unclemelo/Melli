import discord
from discord import app_commands
from discord.ext import commands
import json

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Moderation", custom_id="help_moderation", style=discord.ButtonStyle.primary))
        self.add_item(discord.ui.Button(label="Fun", custom_id="help_fun", style=discord.ButtonStyle.secondary))
        self.add_item(discord.ui.Button(label="Utility", custom_id="help_utility", style=discord.ButtonStyle.success))

# Load commands from JSON file
with open("data/commands.json", "r") as file:
    command_categories = json.load(file)

class ServerConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #show list of available cmds        
    @app_commands.command(name="Command config", description="Changes what commands are allowed on a server")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_cmd(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(title="Server commands permissions",description="cmd - number\ncmd - number",color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Couldent load server specific cmds \nError: {str(e)}")
    
    #depending on the cmd number chosen change its state (true = false, false= true)
    # !NOT DONE!
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            category = interaction.data["custom_id"].split("_")[1].capitalize()
            if category in command_categories:
                embed = discord.Embed(title=f"{category} Commands", description="\n".join(command_categories[category]), color=discord.Color.blurple())
                await interaction.response.edit_message(embed=embed, view=HelpView())

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerConfig(bot))