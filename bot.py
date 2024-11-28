## Libraries
import discord
import os
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

@client.event
async def on_ready():
    """Triggered when the bot is ready."""
    # Sync commands
    try:
        synced_commands = await client.tree.sync()
        print(f"{Fore.GREEN}[ SYNCED ]{Fore.RESET} {len(synced_commands)} commands successfully.")
    except Exception as e:
        print(f"{Fore.RED}[ SYNC FAILED ]{Fore.RESET} {e}")

    # Start updating server count
    update_server_count.start()

    print(f"{Fore.GREEN}[ CONNECTED ]{Fore.RESET} {client.user.name} is online and ready!")
    print(f"Currently in {Fore.BLUE}{len(client.guilds)}{Fore.RESET} guilds.")

@tasks.loop(seconds=10)
async def update_server_count():
    """Updates the bot's presence with the current server count every 10 seconds."""
    try:
        await client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"🦃 | Happy Thanksgiving"
                # {len(client.guilds)} guilds!
            )
        )
    except Exception as e:
        print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Could not update presence: {e}")

## Load Cogs
async def load_cogs():
    """Loads all cog files from the 'cogs' directory."""
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
                print(f"{Fore.GREEN}[ LOADED ]{Fore.RESET} cogs/{filename}")
            except Exception as e:
                print(f"{Fore.RED}[ FAILED TO LOAD ]{Fore.RESET} cogs/{filename}: {e}")

async def main():
    """Main function to initialize the bot."""
    async with client:
        try:
            await load_cogs()
        except Exception as e:
            print(f"{Fore.RED}[ ERROR ]{Fore.RESET} Failed to load cogs: {e}")
        await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
