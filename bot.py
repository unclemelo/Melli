## Libraries
import discord
import os
import asyncio
import requests

from discord.ext import commands, tasks
from dotenv import load_dotenv
from colorama import Fore

## Load Environment Variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK')

## Bot Setup
intents = discord.Intents.all()
client = commands.Bot(command_prefix='mg!', intents=intents)
client.remove_command('help')

status_messages = [
    "🍉 | Reworking Kofinisu's AutoMod...",
    "🌐 | Active in {guild_count} servers!",
    "⚙️ | Type /help for commands!"
]

@client.event
async def on_ready():
    """Triggered when the bot is ready."""
    # Sync commands
    try:
        synced_commands = await client.tree.sync()
        print(f"{Fore.GREEN}[ SYNCED ]{Fore.RESET} {len(synced_commands)} commands successfully.")
    except Exception as e:
        print(f"{Fore.RED}[ SYNC FAILED ]{Fore.RESET} {e}")

    print(f"{Fore.GREEN}[ CONNECTED ]{Fore.RESET} {client.user.name} is online and ready!")
    print(f"Currently in {Fore.BLUE}{len(client.guilds)}{Fore.RESET} guilds.")

    # Start the status update loop
    if not update_status_loop.is_running():
        update_status_loop.start()


@tasks.loop(seconds=10)
async def update_status_loop():
    """Updates the bot's presence with a rotating status every 10 seconds."""
    try:
        guild_count = len(client.guilds)
        current_message = status_messages[update_status_loop.current_loop % len(status_messages)].format(guild_count=guild_count)
        await client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.watching, name=current_message)
        )
    except Exception as e:
        print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Could not update presence: {e}")

def send_webhook_log(message):
    """Sends a log message to the specified Discord webhook."""
    data = {
        "content": message
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code not in range(200, 299):
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Failed to send webhook log: {response.status_code} {response.text}")
    except Exception as e:
        print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Exception while sending webhook log: {e}")

async def load_cogs():
    """Loads all cog files from the 'cogs' directory."""
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
                message = f":white_check_mark: Successfully loaded cog: `{filename}`"
                print(f"{Fore.GREEN}[ LOADED ]{Fore.RESET} cogs/{filename}")
            except Exception as e:
                message = f":x: Failed to load cog: `{filename}`\nError: `{e}`"
                print(f"{Fore.RED}[ FAILED TO LOAD ]{Fore.RESET} cogs/{filename}: {e}")
            finally:
                send_webhook_log(message)

async def main():
    """Main function to initialize the bot."""
    async with client:
        try:
            await load_cogs()
        except Exception as e:
            error_message = f":x: Critical error during cog loading: `{e}`"
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Failed to load cogs: {e}")
            send_webhook_log(error_message)
        await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
