import discord
import datetime
import pytz
import traceback
import sys
import logging
import requests
from discord import app_commands, Interaction
from discord.ext import commands

WEBHOOK_URL = "https://discord.com/api/webhooks/1334413086999838771/7SFMnOltSnpdUxvbNjIV8rud6jmogrrTm559U79_0LgAmmxkOHFvc23akJz304VjfuXk"

class ERROR(commands.Cog):
    def __init__(self, bot: commands.Bot, error_channel_id: int):
        self.bot = bot
        self.error_channel_id = error_channel_id
        self.bot.tree.on_error = self.global_app_command_error

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler("bot_errors.log"), logging.StreamHandler()]
        )

        # Redirect stdout & stderr
        sys.stdout = self
        sys.stderr = self

        # Handle uncaught exceptions
        sys.excepthook = self.handle_uncaught_exception

    async def global_app_command_error(self, interaction: Interaction, error: Exception):
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
                "An unexpected error occurred. The devs have been notified.",
                ephemeral=True
            )

            # Gather error details
            error_type = type(error).__name__
            traceback_details = "".join(traceback.format_exception(type(error), error, error.__traceback__))

            # Logging to console and file
            logging.error(f"Unhandled Exception: {traceback_details}")

            # Send to webhook
            self.send_to_webhook(f"**[ERROR]** {error_type}: ```py\n{traceback_details[:1900]}```")

    def handle_uncaught_exception(self, exctype, value, tb):
        """Logs any uncaught exceptions and sends to webhook."""
        traceback_details = "".join(traceback.format_exception(exctype, value, tb))
        logging.critical(f"Uncaught Exception: {traceback_details}")

        self.send_to_webhook(f"**[CRITICAL ERROR]** ```py\n{traceback_details[:1900]}```")

    def send_to_webhook(self, message):
        """Sends logs to the Melli Console webhook using requests."""
        payload = {"content": message, "username": "Melli Console"}
        try:
            response = requests.post(WEBHOOK_URL, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send log to webhook: {e}")

    def write(self, message):
        """Redirects print() and errors to the webhook."""
        message = message.strip()
        if message:
            logging.info(message)  # Log to file
            self.send_to_webhook(f"**[LOG]** ```{message[:1900]}```")

    def flush(self):
        """Required for sys.stdout override."""
        pass

async def setup(bot: commands.Bot):
    error_channel_id = 1308048388637462558
    await bot.add_cog(ERROR(bot, error_channel_id))
