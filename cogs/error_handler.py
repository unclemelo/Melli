import discord
import datetime
import pytz
import traceback
import sys
import logging
import requests
import os
from discord import app_commands, Interaction
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK')

class ERROR(commands.Cog):
    def __init__(self, bot: commands.Bot, error_channel_id: int):
        self.bot = bot
        self.error_channel_id = error_channel_id

        # Global error handler for slash commands
        self.bot.tree.on_error = self.global_app_command_error

        # Global handler for async background task errors
        self.bot.loop.set_exception_handler(self.handle_async_exception)

        # Logging config
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler("bot_errors.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        # Redirect stdout and stderr
        sys.stdout = self
        sys.stderr = self
        sys.excepthook = self.handle_uncaught_exception

    async def global_app_command_error(self, interaction: Interaction, error: Exception):
        """
        Handles errors in slash commands.
        """
        error_type = type(error).__name__
        error_message = str(error)

        # Send user-friendly message
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⌛ Please wait! Try again in **{error.retry_after:.2f}** seconds.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "🚫 You don't have permission to use this command.",
                ephemeral=True
            )
        else:
            # Ensure the interaction is responded to
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An unexpected error occurred. The developers have been notified.",
                    ephemeral=True
                )

            # Log full traceback
            trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            logging.error(f"Unhandled Slash Command Exception:\n{trace}")
            self.send_to_webhook(f"**[SLASH ERROR]** `{error_type}`\n```py\n{trace[:1900]}\n```")

    def handle_async_exception(self, loop, context):
        """
        Handles background task exceptions (not tied to commands).
        """
        error = context.get("exception")
        if error:
            trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            error_type = type(error).__name__
            logging.critical(f"Unhandled Async Exception:\n{trace}")
            self.send_to_webhook(f"**[ASYNC ERROR]** `{error_type}`\n```py\n{trace[:1900]}\n```")
        else:
            message = context.get("message", "Unknown async error")
            logging.critical(f"Unhandled Async Error: {message}")
            self.send_to_webhook(f"**[ASYNC ERROR]** {message}")

    def handle_uncaught_exception(self, exctype, value, tb):
        """
        Handles uncaught synchronous exceptions.
        """
        trace = "".join(traceback.format_exception(exctype, value, tb))
        error_type = exctype.__name__
        logging.critical(f"Uncaught Exception:\n{trace}")
        self.send_to_webhook(f"**[CRITICAL ERROR]** `{error_type}`\n```py\n{trace[:1900]}\n```")

    def send_to_webhook(self, message):
        """
        Sends a message to the webhook for remote logging.
        """
        payload = {
            "content": message,
            "username": "Melli Console",
            "avatar_url": "https://cdn.discordapp.com/attachments/1308048388637462558/1335601521550692392/1200px-GNOME_Terminal_icon_2019.png"
        }
        try:
            response = requests.post(WEBHOOK_URL, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send log to webhook: {e}")

    def write(self, message):
        """
        Redirects print() and standard output to log + webhook.
        """
        message = message.strip()
        if message:
            logging.info(message)
            self.send_to_webhook(f"**[LOG]** `{message[:1900]}`")

    def flush(self):
        """Required method for file-like objects."""
        pass

async def setup(bot: commands.Bot):
    # Replace this with your actual error logging channel ID if needed
    error_channel_id = 1308048388637462558
    await bot.add_cog(ERROR(bot, error_channel_id))
