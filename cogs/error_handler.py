import discord
import traceback
import sys
import logging
import requests
import os
from discord import app_commands, Interaction
from discord.ext import commands
from dotenv import load_dotenv

# Load .env for webhook
load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK')

class ERROR(commands.Cog):
    def __init__(self, bot: commands.Bot, error_channel_id: int):
        self.bot = bot
        self.error_channel_id = error_channel_id

        # Assign global app command error handler
        self.bot.tree.on_error = self.global_app_command_error

        # Set up logging to file and console
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler("bot_errors.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        # Redirect print() and errors
        sys.stdout = self
        sys.stderr = self
        sys.excepthook = self.handle_uncaught_exception

    async def cog_load(self):
        """
        Called when the cog is fully loaded and bot is initialized.
        Safe place to access loop.
        """
        self.bot.loop.set_exception_handler(self.handle_async_exception)

    async def global_app_command_error(self, interaction: Interaction, error: Exception):
        """
        Handles errors from slash commands.
        """
        error_type = type(error).__name__
        error_message = str(error)

        # User-facing response
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⌛ This command is on cooldown. Try again in **{error.retry_after:.2f}** seconds.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "🚫 You do not have permission to use this command.",
                ephemeral=True
            )
        else:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An unexpected error occurred. The developers have been notified.",
                    ephemeral=True
                )

            # Full traceback
            trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            logging.error(f"Unhandled Slash Command Exception:\n{trace}")
            self.send_to_webhook(f"**[SLASH ERROR]** `{error_type}`\n```py\n{trace[:1900]}\n```")

    def handle_async_exception(self, loop, context):
        """
        Handles unhandled errors in async tasks.
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
        Logs uncaught sync exceptions and sends to webhook.
        """
        trace = "".join(traceback.format_exception(exctype, value, tb))
        error_type = exctype.__name__
        logging.critical(f"Uncaught Exception:\n{trace}")
        self.send_to_webhook(f"**[CRITICAL ERROR]** `{error_type}`\n```py\n{trace[:1900]}\n```")

    def send_to_webhook(self, message):
        """
        Sends formatted message to Discord webhook.
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
        Redirects print() and stdout to logging and webhook.
        """
        message = message.strip()
        if message:
            logging.info(message)
            self.send_to_webhook(f"**[LOG]** `{message[:1900]}`")

    def flush(self):
        pass

# Bot extension setup
async def setup(bot: commands.Bot):
    error_channel_id = 1308048388637462558  # Replace with your error channel ID if needed
    await bot.add_cog(ERROR(bot, error_channel_id))
