import discord
import traceback
import sys
import logging
import requests
import os
from discord import app_commands, Interaction
from discord.ext import commands
from dotenv import load_dotenv

# Load .env for webhook URL
load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK')

class ERROR(commands.Cog):
    def __init__(self, bot: commands.Bot, error_channel_id: int):
        self.bot = bot
        self.error_channel_id = error_channel_id

        # Assign global slash command error handler
        self.bot.tree.on_error = self.global_app_command_error

        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler("bot_errors.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        # Redirect stdout, stderr, uncaught exceptions to custom handlers
        sys.stdout = self
        sys.stderr = self
        sys.excepthook = self.handle_uncaught_exception

    async def global_app_command_error(self, interaction: Interaction, error: Exception):
        """
        Slash command error handler responding in server + sending to webhook.
        """
        error_type = type(error).__name__
        trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        # Handle common user errors gracefully
        if isinstance(error, CommandOnCooldown):
            await interaction.response.send_message(
                f"⌛ This command is on cooldown. Try again in **{error.retry_after:.2f}** seconds.",
                ephemeral=True
            )
        elif isinstance(error, MissingPermissions):
            await interaction.response.send_message(
                "🚫 You do not have permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, BotMissingPermissions):
            await interaction.response.send_message(
                "⚠️ I don't have the required permissions to execute this command.",
                ephemeral=True
            )
        elif isinstance(error, MissingRole):
            await interaction.response.send_message(
                f"🔐 You must have the `{error.missing_role}` role to use this command.",
                ephemeral=True
            )
        elif isinstance(error, MissingAnyRole):
            missing = ", ".join(f"`{role}`" for role in error.missing_roles)
            await interaction.response.send_message(
                f"🔐 You need at least one of the following roles to use this command: {missing}.",
                ephemeral=True
            )
        elif isinstance(error, NoPrivateMessage):
            await interaction.response.send_message(
                "📵 This command cannot be used in DMs.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "❌ You don't meet the requirements to run this command.",
                ephemeral=True
            )
        # For other errors, notify user and log
        elif not interaction.response.is_done():
            try:
                await interaction.response.send_message(
                    "❌ An unexpected error occurred. The developers have been notified.",
                    ephemeral=False
                )
            except discord.HTTPException:
                pass  # in case response already sent or can't send

        # Prepare detailed message for webhook
        user = interaction.user
        command = interaction.command.name if interaction.command else "Unknown"
        guild = interaction.guild.name if interaction.guild else "DMs"

        self.send_to_webhook(
            f"**[SLASH ERROR]** `{error_type}` in command `/{command}`\n"
            f"User: {user} (`{user.id}`)\n"
            f"Guild: {guild}\n"
            f"```py\n{trace[:1900]}\n```"
        )

    def handle_uncaught_exception(self, exctype, value, tb):
        """
        Log uncaught sync exceptions and send to webhook.
        """
        trace = "".join(traceback.format_exception(exctype, value, tb))
        self.send_to_webhook(f"**[CRITICAL ERROR]** `{exctype.__name__}`\n```py\n{trace[:1900]}\n```")
        logging.critical(f"Uncaught Exception:\n{trace}")

    def send_to_webhook(self, message: str):
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

    def write(self, message: str):
        """
        Redirect print() and stdout to logging and webhook.
        """
        message = message.strip()
        if message:
            logging.info(message)
            self.send_to_webhook(f"**[LOG]** `{message[:1900]}`")

    def flush(self):
        pass

# Cog setup
async def setup(bot: commands.Bot):
    await bot.add_cog(ERROR(bot, error_channel_id=1308048388637462558))
