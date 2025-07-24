import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import asyncio

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actions = [
            "hug", "pat", "slap", "kiss", "cuddle", "poke",
            "highfive", "bite", "tickle", "boop", "snuggle"
        ]

    async def fetch_gif(self, action: str) -> str:
        return await self._try_apis(action)

    async def _try_apis(self, action: str) -> str:
        apis = [self._from_waifu_pics, self._from_nekos_best]

        for api_func in apis:
            try:
                gif_url = await api_func(action)
                if gif_url:
                    return gif_url
            except Exception as e:
                print(f"[WARN] {api_func.__name__} failed: {e}")
        return None

    async def _from_waifu_pics(self, action: str) -> str:
        url = f"https://api.waifu.pics/sfw/{action}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("url")

    async def _from_nekos_best(self, action: str) -> str:
        url = f"https://nekos.best/api/v2/{action}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["results"][0]["url"]

    @app_commands.command(name="interact", description="Interact with someone using a fun anime action!")
    @app_commands.describe(action="Choose an action", user="The user to interact with")
    @app_commands.choices(
        action=[app_commands.Choice(name=a.title(), value=a) for a in [
            "hug", "pat", "slap", "kiss", "cuddle", "poke",
            "highfive", "bite", "snuggle"
        ]]
    )
    async def interact(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        user: discord.User
    ):
        await interaction.response.defer()

        if user.id == interaction.user.id:
            return await interaction.followup.send(
                f"🤔 You can't {action.name} yourself... but nice try!",
                ephemeral=True
            )

        if user.id == self.bot.user.id:
            user_to_bot_gif = await self.fetch_gif(action.value)
            bot_to_user_gif = await self.fetch_gif(action.value)

            if not user_to_bot_gif or not bot_to_user_gif:
                return await interaction.followup.send(
                    "❌ Couldn't fetch GIFs. Please try again later.", ephemeral=True
                )

            embed1 = discord.Embed(
                title=f"{interaction.user.display_name} {action.name}s {self.bot.user.display_name}!",
                color=discord.Color.random()
            )
            embed1.set_image(url=user_to_bot_gif)
            embed1.set_footer(text="Bold move...")

            await interaction.followup.send(embed=embed1)
            await asyncio.sleep(2)

            embed2 = discord.Embed(
                title=f"{self.bot.user.display_name} {action.name}s {interaction.user.display_name} back!",
                color=discord.Color.random()
            )
            embed2.set_image(url=bot_to_user_gif)
            embed2.set_footer(text="h-h-how could you T///T I'm just a bot.")

            await interaction.followup.send(embed=embed2)
            return

        gif_url = await self.fetch_gif(action.value)
        if not gif_url:
            return await interaction.followup.send(
                "❌ Failed to fetch GIF. Try again later.", ephemeral=True
            )

        class InteractBackButton(discord.ui.View):
            def __init__(self, cog: commands.Cog, action: str, user: discord.User, target: discord.User):
                super().__init__(timeout=60)
                self.cog = cog
                self.action = action
                self.user = user
                self.target = target
                self.button_used = False
                self.message = None

            @discord.ui.button(label="Interact back", style=discord.ButtonStyle.blurple)
            async def interact_back(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                if interaction_button.user.id != self.target.id:
                    return await interaction_button.response.send_message(
                        "❌ Only the tagged user can interact back!", ephemeral=True
                    )

                reply_gif = await self.cog.fetch_gif(self.action)
                if not reply_gif:
                    return await interaction_button.response.send_message(
                        "❌ Couldn't fetch a GIF for your response.", ephemeral=True
                    )

                embed = discord.Embed(
                    title=f"{self.target.display_name} {self.action}s {self.user.display_name} back!",
                    color=discord.Color.random()
                )
                embed.set_image(url=reply_gif)
                embed.set_footer(text="Beta feature request by Vpitedree")
                await interaction_button.response.send_message(embed=embed)

                self.button_used = True
                for child in self.children:
                    child.disabled = True
                await interaction_button.message.edit(view=self)

            async def on_timeout(self):
                if not self.button_used and self.message:
                    for child in self.children:
                        child.disabled = True
                    try:
                        await self.message.edit(view=self)
                    except:
                        pass

        embed = discord.Embed(
            title=f"{interaction.user.display_name} {action.name}s {user.display_name}!",
            color=discord.Color.random()
        )
        embed.set_image(url=gif_url)
        embed.set_footer(text="Beta feature request by Vpitedree")

        view = InteractBackButton(self, action.value, interaction.user, user)
        message = await interaction.followup.send(embed=embed, view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(Social(bot))
