import discord
import traceback
import logging
import sys
from discord import app_commands, Interaction
from discord.ext import commands
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

class ERROR(commands.Cog):
    def __init__(self, bot: commands.Bot, error_channel_id: int):
        self.bot = bot
        self.error_channel_id = error_channel_id

        # Assign global slash command error handler
        self.bot.tree.on_error = self.global_app_command_error

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler("bot_errors.log", encoding="utf-8"),
                logging.StreamHandler(sys.__stdout__)  # use original stdout
            ]
        )

        # Global exception hook
        sys.excepthook = self.handle_uncaught_exception

    async def global_app_command_error(self, interaction: Interaction, error: Exception):
        """
        Handles errors from slash commands (app_commands).
        """
        error_type = type(error).__name__
        trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        # ✅ User-friendly messages
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⌛ This command is on cooldown. Try again in **{error.retry_after:.2f}** seconds."
        elif isinstance(error, app_commands.MissingPermissions):
            msg = "🚫 You do not have permission to use this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            msg = "⚠️ I don't have the required permissions to execute this command."
        elif isinstance(error, app_commands.MissingRole):
            msg = f"🔐 You must have the `{error.missing_role}` role to use this command."
        elif isinstance(error, app_commands.MissingAnyRole):
            missing = ", ".join(f"`{role}`" for role in error.missing_roles)
            msg = f"🔐 You need at least one of the following roles to use this command: {missing}."
        elif isinstance(error, app_commands.NoPrivateMessage):
            msg = "📵 This command cannot be used in DMs."
        elif isinstance(error, app_commands.CheckFailure):
            msg = "❌ You don't meet the requirements to run this command."
        else:
            msg = "❌ An unexpected error occurred. The developers have been notified."

        # ✅ Show message to the user
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)
        except discord.HTTPException:
            pass

        # 🖨️ Pretty error printout in console
        user = interaction.user
        command = interaction.command.name if interaction.command else "Unknown"
        guild = interaction.guild.name if interaction.guild else "DMs"

        formatted_error = (
            f"\n{Fore.RED}{Style.BRIGHT}[SLASH ERROR] {Fore.YELLOW}{error_type}\n"
            f"{Fore.CYAN}Command: {Fore.WHITE}/{command}\n"
            f"{Fore.CYAN}User: {Fore.WHITE}{user} ({user.id})\n"
            f"{Fore.CYAN}Guild: {Fore.WHITE}{guild}\n"
            f"{Fore.MAGENTA}Traceback:\n{Fore.WHITE}{trace}"
        )

        print(formatted_error)
        logging.error(f"[SLASH ERROR] {error_type} in /{command}\n{trace}")

    def handle_uncaught_exception(self, exctype, value, tb):
        if exctype is KeyboardInterrupt:
            print(f"{Fore.YELLOW}[!] KeyboardInterrupt detected. Exiting gracefully.")
            return

        trace = "".join(traceback.format_exception(exctype, value, tb))
        formatted_trace = (
            f"\n{Fore.RED}{Style.BRIGHT}[CRITICAL ERROR] {Fore.YELLOW}{exctype.__name__}\n"
            f"{Fore.MAGENTA}Traceback:\n{Fore.WHITE}{trace}"
        )

        print(formatted_trace)
        logging.critical(f"Uncaught Exception:\n{trace}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ERROR(bot, error_channel_id=1308048388637462558))
