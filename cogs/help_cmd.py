import discord
from discord.ext import commands
from discord import app_commands
from typing import List

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows the list of commands categorized")
    async def helpcmd(self, interaction: discord.Interaction):
        """Displays an interactive help menu with categorized commands."""

        try:
            # Define command categories
            command_categories = {
                "Moderation": ["</ban:1330966727948894299>", "</kick:1330966727948894300>", "</mute:1331002213983846452>", "</unmute:1331002213983846453>", "</warn:1330897980462600299>", "</warnings:1330897980462600300>", "</clear:1331002213983846454>", "</clearwarns:1330897980945076267>", "</delwarn:1330897980945076266>", "</unban:1331002213983846450>"],
                "Fun": ["</chaos:1326163954531176572>", "</cheese:1331705714950803496>", "</knockout:1326163954531176570>", "</prank:1326163954531176573>", "</revive:1326163954531176571>", "</votekick:1328523711216881716>", "</credits:1331872616163704874>"],
                "Utility": ["</setup_automod:1331023235726180447>", "</update_automod:1331023235726180449>", "</uptime:1321819862628302920>", "</reboot:1316240452038561814> - **Dev Only**", "</shutdown:1321819862628302919> - **Dev Only**"]
            }

            # Build the embeds
            embeds = []
            for category, commands in command_categories.items():
                embed = discord.Embed(
                    title=f"Help: {category}",
                    description="\n".join(commands),
                    color=0x3474eb
                )
                embed.set_footer(text="Use the buttons below to navigate.")
                embeds.append(embed)

            # Button navigation
            class HelpView(discord.ui.View):
                def __init__(self, embeds: List[discord.Embed]):
                    super().__init__(timeout=60)
                    self.embeds = embeds
                    self.current_page = 0

                async def update_embed(self, interaction: discord.Interaction):
                    await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

                @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
                async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = (self.current_page - 1) % len(self.embeds)
                    await self.update_embed(interaction)

                @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
                async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = (self.current_page + 1) % len(self.embeds)
                    await self.update_embed(interaction)

            # Send the first embed with the interactive view
            await interaction.response.send_message(embed=embeds[0], view=HelpView(embeds), ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while generating the help menu. Please contact an administrator.\n```{e}```",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
