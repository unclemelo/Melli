import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actions = [
            "hug", "pat", "slap", "kiss", "cuddle", "poke",
            "highfive", "bite", "tickle", "boop", "snuggle"
        ]

    async def fetch_gif(self, action: str) -> str:
        url = f"https://api.waifu.pics/sfw/{action}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["url"]
                return None

    @app_commands.command(name="interact", description="Interact with someone using a fun anime action!")
    @app_commands.describe(action="Choose an action", user="The user to interact with")
    @app_commands.choices(
        action=[app_commands.Choice(name=a.title(), value=a) for a in [
            "hug", "pat", "slap", "kiss", "cuddle", "poke",
            "highfive", "bite", "tickle", "boop", "snuggle"
        ]]
    )
    async def interact(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        user: discord.User
    ):
        if user.id == interaction.user.id:
            return await interaction.response.send_message(
                f"🤔 You can't {action.name} yourself... but nice try!",
                ephemeral=True
            )

        gif_url = await self.fetch_gif(action.value)
        if not gif_url:
            return await interaction.response.send_message(
                "❌ Failed to fetch GIF. Try again later.", ephemeral=True
            )

        # Button view class
        class InteractBackButton(discord.ui.View):
            def __init__(self, cog: commands.Cog, action: str, user: discord.User, target: discord.User):
                super().__init__(timeout=60)
                self.cog = cog
                self.action = action
                self.user = user
                self.target = target

            @discord.ui.button(label="Interact back", style=discord.ButtonStyle.blurple)
            async def interact_back(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                reply_gif = await self.cog.fetch_gif(self.action)
                embed = discord.Embed(
                    title=f"{self.target.display_name} {self.action}s {self.user.display_name} back!",
                    color=discord.Color.random()
                )
                embed.set_image(url=reply_gif)
                embed.set_footer(text="Beta feature request by Vpitedree")
                await interaction_button.response.send_message(embed=embed)

        embed = discord.Embed(
            title=f"{interaction.user.display_name} {action.name}s {user.display_name}!",
            color=discord.Color.random()
        )
        embed.set_image(url=gif_url)
        embed.set_footer(text="Beta feature request by Vpitedree")

        view = InteractBackButton(
            cog=self,
            action=action.value,
            user=interaction.user,
            target=user
        )

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Social(bot))
