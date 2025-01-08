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
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"Take a chill pill! Command is cooling off. Try again in **{error.retry_after:.2f}** seconds.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "LOL, you thought? Not enough perms, buddy.",
                ephemeral=True
            )
        else:

            await interaction.response.send_message(
                "There was an unexpected error, we have sent the errors to the devs of the bot.\nThey will work a on a patch soon.",
                ephemeral=True
            )
            # Gather error details
            error_type = type(error).__name__
            traceback_details = "".join(traceback.format_exception(type(error), error, error.__traceback__))

            # Primary embed: Summary of the error
            summary_embed = discord.Embed(
                title="Command Error",
                description=f"An error occurred in the following command: `{interaction.command}`",
                color=discord.Color.red(),
            )
            summary_embed.add_field(name="Error Type", value=f"`{error_type}`", inline=False)
            summary_embed.add_field(
                name="Error Message",
                value=f"```ansi\n[2;31m{str(error)}\n[0m[2;31m[0m```",
                inline=False,
            )

            if interaction.user:
                summary_embed.add_field(
                    name="User",
                    value=f"Name: `{interaction.user}`\nID: `{interaction.user.id}`",
                    inline=False,
                )

            if interaction.guild:
                summary_embed.add_field(
                    name="Guild",
                    value=f"Name: `{interaction.guild.name}`\nID: `{interaction.guild.id}`",
                    inline=False,
                )

            utc_time = datetime.datetime.utcnow()
            target_timezone = pytz.timezone('America/Chicago')
            cst_time = utc_time.replace(tzinfo=pytz.utc).astimezone(target_timezone)

            summary_embed.set_footer(text=f"{cst_time.strftime('%m/%d/%Y | %H:%M%p [CST]')}")
            summary_embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1255215236370141236/1255216537376129127/1200px-No_icon_28white_X_on_red_circle29.png"
            )

            # Secondary embed: Traceback details
            traceback_embed = discord.Embed(
                title="Error Traceback",
                description=f"```py\n{traceback_details[:3900]}```",  # Discord has a 4000 character limit; truncate if needed
                color=discord.Color.dark_red(),
            )
            traceback_embed.set_footer(text="Truncated if too long.")

            # Send to the specified error channel
            error_channel = self.bot.get_channel(self.error_channel_id)
            if error_channel:
                await error_channel.send(embeds=[summary_embed, traceback_embed])
            else:
                print("Error occurred but could not send to the specified error channel.")
                print(traceback_details)

async def setup(bot: commands.Bot):
    error_channel_id = 1308048388637462558
    await bot.add_cog(ERROR(bot, error_channel_id))
