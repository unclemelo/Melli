## Libraries
import discord
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
from colorama import Fore

## Load Environment Variables
load_dotenv()
TOKEN = os.getenv('TOKEN')

## Bot Setup
intents = discord.Intents.all()
client = commands.Bot(command_prefix='mg!', intents=intents)
client.remove_command('help')

status_messages = [
    "🍉 | Under Maintence",
    "🌐 | Active in {guild_count} servers!",
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
        # Static data
        guild_count = len(client.guilds)

        # Combine static and dynamic statuses
        all_status_messages = status_messages

        # Cycle through messages
        current_message = all_status_messages[update_status_loop.current_loop % len(all_status_messages)].format(guild_count=guild_count)
        await client.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(type=discord.ActivityType.watching, name=current_message)
        )
    except Exception as e:
        print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Could not update presence: {e}")


async def main():
    """Main function to initialize the bot."""
    await client.start(TOKEN)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
