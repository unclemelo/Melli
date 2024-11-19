import discord
import datetime
import pytz
from discord import app_commands, Interaction
from discord.ext import commands

class ERROR(commands.Cog):
    def __init__(self, bot: commands.Bot, error_channel_id: int):
        self.bot = bot
        self.error_channel_id = error_channel_id
        self.bot.tree.on_error = self.global_app_command_error

    async def global_app_command_error(
        self, interaction: Interaction, error: Exception
    ):
        embed = discord.Embed(
            title="Command Error",
            description=f"An error occurred in the following command: `{interaction.command}`",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Error",
            value=f"```ansi\n[2;31m{str(error)}\n[0m[2;31m[0m```",
            inline=False,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1255215236370141236/1255216537376129127/1200px-No_icon_28white_X_on_red_circle29.png?ex=667c52ff&is=667b017f&hm=91371407f058f63b6094ea4f35e5f94f704c23f24addd83e3b128bbeb96a6b6a&"
        )

        utc_time = datetime.datetime.utcnow()

        target_timezone = pytz.timezone('America/Chicago')

        cst_time = utc_time.replace(tzinfo=pytz.utc).astimezone(target_timezone)

        embed.set_footer(text=f"{cst_time.strftime('%m/%d/%Y | %H:%M%p [CST]')}")
        error_channel = self.bot.get_channel(self.error_channel_id)
        if error_channel:
            await error_channel.send(embed=embed)
        else:
            print(f"Error: {error}")

    @app_commands.command(name="simulate_error", description="Testing errors")
    @app_commands.checks.has_permissions(administrator=True)
    async def simulate_error(self, interaction: discord.Interaction):
        raise RuntimeError("This is a simulated error.")

async def setup(bot: commands.Bot):
    error_channel_id = 1308048388637462558
    await bot.add_cog(ERROR(bot, error_channel_id))
