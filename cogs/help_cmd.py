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
                "Moderation": ["/ban", "/kick", "/mute", "/unmute", "/warn", "/warnings", "/clear", "/clearwarns", "/delwarn", "/unban"],
                "Fun": ["/chaos", "cheese", "/knockout", "/prank", "/revive", "/votekick"],
                "Utility": ["/setup_automod", "/update_automod", "/uptime", "/reboot", "/shutdown"]
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

                @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
                async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.message.delete()

            # Send the first embed with the interactive view
            await interaction.response.send_message(embed=embeds[0], view=HelpView(embeds), ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while generating the help menu. Please contact an administrator.\n```{e}```",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
