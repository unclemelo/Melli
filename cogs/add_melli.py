import discord
from discord import app_commands
from discord.ext import commands
from util.command_checks import command_enabled

class AddMelli(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add_melli", description="Invite Melli and view her credits!")
    @command_enabled()
    async def add_melli(self, interaction: discord.Interaction):

        try:
            # Invite button
            invite_url = "https://discord.com/oauth2/authorize?client_id=1316235145778434070&permissions=8&integration_type=0&scope=bot"
            github_url = "https://github.com/unclemelo/Melli"
            view = discord.ui.View()
            button = discord.ui.Button(label="➕ Add Melli", url=invite_url, style=discord.ButtonStyle.link)
            githubbutton = discord.ui.Button(label="<:github:1372632557945880606> GitHub", url=github_url, style=discord.ButtonStyle.link)
            view.add_item(button)
            view.add_item(githubbutton)

            # Embed with credits and invite prompt
            embed = discord.Embed(
                title="✨ Meet Melli ✨",
                description="A heartfelt thank you to everyone who contributed to Melli!\n\n**<:vwv:1323527766011809873> Click the button below to invite Melli to your server!**",
                color=0x5865F2
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1308048258337345609/1331874809352556597/f0a534c6da023d46a18674bcf5a6a147.png")
            embed.add_field(
                name="👨‍💻 Developers", 
                value="> `@_uncle_melo_`, `@pitr1010`, `@illtana`", 
                inline=False
            )
            embed.add_field(
                name="✍️ Editor", 
                value="> `@mizuki_mochizuki2090`", 
                inline=False
            )
            embed.add_field(
                name="🎨 Artists", 
                value="> `@soupinascoop`, `@bunnnl`", 
                inline=False
            )
            embed.set_footer(
                text="Thanks for supporting Melli!",
                icon_url="https://cdn.discordapp.com/emojis/1323527766011809873.webp"
            )

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred. Please contact an administrator.\n```{e}```", 
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(AddMelli(bot))

