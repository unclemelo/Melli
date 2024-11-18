## Libs
import discord, os, asyncio

from itertools import cycle
from discord.ext import commands, tasks
from dotenv import load_dotenv
from colorama import Fore

## ^//~//^ I love python

load_dotenv()
token = os.getenv('TOKEN')


client = commands.Bot(command_prefix='mg!', intents=discord.Intents.all())
client.remove_command('help')


@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except Exception as e:
        print(f'already synced\n{Fore.RED}[ FAILED ]{Fore.RESET} {e}')
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"🍉 {len(client.guilds)} guilds!"))
    print(f"{Fore.GREEN}Connected to {client.user.name}!{Fore.RESET}")

# Load cogs
async def load_cogs():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        try:
            await load_cogs()
        except Exception as e:
            print(f"Error loading cogs: {e}")
        await client.start(token)

asyncio.run(main())
