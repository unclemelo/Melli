import discord
import datetime
import pytz
import traceback
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
        # Gather error details
        error_type = type(error).__name__
        traceback_details = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        embed = discord.Embed(
            title="Command Error",
            description=f"An error occurred in the following command: `{interaction.command}`",
            color=discord.Color.red(),
        )
        embed.add_field(name="Error Type", value=f"`{error_type}`", inline=False)
        embed.add_field(
            name="Error Message",
            value=f"```ansi\n[2;31m{str(error)}\n[0m[2;31m[0m```",
            inline=False,
        )
        embed.add_field(
            name="Traceback",
            value=f"```py\n{traceback_details[:400]}```",  # Truncate if too long
            inline=False,
        )

        if interaction.user:
            embed.add_field(
                name="User",
                value=f"Name: `{interaction.user}`\nID: `{interaction.user.id}`",
                inline=False,
            )

        if interaction.guild:
            embed.add_field(
                name="Guild",
                value=f"Name: `{interaction.guild.name}`\nID: `{interaction.guild.id}`",
                inline=False,
            )

        utc_time = datetime.datetime.utcnow()
        target_timezone = pytz.timezone('America/Chicago')
        cst_time = utc_time.replace(tzinfo=pytz.utc).astimezone(target_timezone)

        embed.set_footer(text=f"{cst_time.strftime('%m/%d/%Y | %H:%M%p [CST]')}")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1255215236370141236/1255216537376129127/1200px-No_icon_28white_X_on_red_circle29.png"
        )

        # Send to the specified error channel
        error_channel = self.bot.get_channel(self.error_channel_id)
        if error_channel:
            await error_channel.send(embed=embed)
        else:
            print(f"Error occurred but could not send to channel:\n{traceback_details}")

    @app_commands.command(name="simulate_error", description="Testing errors")
    @app_commands.checks.has_permissions(administrator=True)
    async def simulate_error(self, interaction: discord.Interaction):
        raise RuntimeError("This is a simulated error.")

async def setup(bot: commands.Bot):
    error_channel_id = 1308048388637462558
    await bot.add_cog(ERROR(bot, error_channel_id))
