import discord
from discord.ext import commands
from twitch_queue import twitch_queue

class TwitchModPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        if interaction.data["custom_id"].startswith("timeout:"):
            user = interaction.data["custom_id"].split(":")[1]
            await interaction.response.send_message(f"⏳ Sending timeout for `{user}`...", ephemeral=True)
            await twitch_queue.put(("timeout", user))

async def setup(bot):
    await bot.add_cog(TwitchModPanel(bot))
