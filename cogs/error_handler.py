import discord
import datetime
import pytz
import traceback
import sys
import logging
import requests
from discord import app_commands, Interaction
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK')

class ERROR(commands.Cog):
    def __init__(self, bot: commands.Bot, error_channel_id: int):
        # Initialize the cog with bot and error channel ID
        self.bot = bot
        self.error_channel_id = error_channel_id
        self.bot.tree.on_error = self.global_app_command_error  # Global error handler for app commands

        # Set up logging for both console and file
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler("bot_errors.log"), logging.StreamHandler()]
        )

        # Redirect stdout & stderr to log messages automatically
        sys.stdout = self
        sys.stderr = self

        # Handle uncaught exceptions globally
        sys.excepthook = self.handle_uncaught_exception

    async def global_app_command_error(self, interaction: Interaction, error: Exception):
        """
        Handles errors for application commands (slash commands) that occur during execution.
        """
        if isinstance(error, app_commands.CommandOnCooldown):
            # If the command is on cooldown
            await interaction.response.send_message(
                f"Please wait! Command is cooling off. Try again in **{error.retry_after:.2f}** seconds.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            # If the user lacks necessary permissions
            await interaction.response.send_message(
                "You don't have the required permissions to use this command.",
                ephemeral=True
            )
        else:
            # For any unexpected error, notify the user and log the error details
            await interaction.response.send_message(
                "An unexpected error occurred. The developers have been notified.",
                ephemeral=True
            )

            # Gather and log error details (only error type and part of the traceback)
            error_type = type(error).__name__
            error_message = str(error)

            # Log the error to both console and the error log file
            logging.error(f"Unhandled Exception: {error_type} - {error_message}")

            # Send error details (error type + message) to the webhook
            self.send_to_webhook(f"**[ERROR]** {error_type}: `{error_message[:1900]}`")

    def handle_uncaught_exception(self, exctype, value, tb):
        """
        Logs any uncaught exceptions and sends details to a webhook.
        """
        # Extract just the error type and message, not the full traceback
        error_type = exctype.__name__
        error_message = str(value)
        logging.critical(f"Uncaught Exception: {error_type} - {error_message}")

        # Send uncaught exception details to the webhook
        self.send_to_webhook(f"**[CRITICAL ERROR]** {error_type}: `{error_message[:1900]}`")

    def send_to_webhook(self, message):
        """
        Sends log messages to a Discord webhook for monitoring.
        """
        payload = {
            "content": message,
            "username": "Melli Console",
            "avatar_url": "https://cdn.discordapp.com/attachments/1308048388637462558/1335601521550692392/1200px-GNOME_Terminal_icon_2019.png"
        }
        try:
            # Send the log message to the webhook URL
            response = requests.post(WEBHOOK_URL, json=payload)
            response.raise_for_status()  # Raise an exception if the request failed
        except requests.exceptions.RequestException as e:
            # Log an error if the webhook message fails to send
            logging.error(f"Failed to send log to webhook: {e}")

    def write(self, message):
        """
        Redirects print statements and errors to the logging system and webhook.
        """
        message = message.strip()
        if message:
            logging.info(message)  # Log the message to the log file
            self.send_to_webhook(f"**[SYSTEM LOG]** `{message[:1900]}`")

    def flush(self):
        """
        This is required to fulfill the interface for redirecting sys.stdout and sys.stderr.
        It doesn't need to do anything.
        """
        pass

async def setup(bot: commands.Bot):
    # The error channel ID can be set dynamically, but it's hardcoded here for simplicity
    error_channel_id = 1308048388637462558
    await bot.add_cog(ERROR(bot, error_channel_id))  # Add the ERROR cog to the bot
