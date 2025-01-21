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

async def send_webhook_log(embed: discord.Embed):
    """Sends an embed message to the specified webhook."""
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(WEBHOOK_URL, adapter=AsyncWebhookAdapter(session))
        await webhook.send(embed=embed)


async def load_cogs():
    """Loads all cog files from the 'cogs' directory and logs the results using a webhook."""
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            embed = discord.Embed()
            embed.set_footer(text="Cog Loader")

            try:
                await client.load_extension(f'cogs.{filename[:-3]}')
                embed.title = "✅ Cog Loaded Successfully"
                embed.description = f"Successfully loaded cog: `{filename}`"
                embed.color = discord.Color.green()
                print(f"{Fore.GREEN}[ LOADED ]{Fore.RESET} cogs/{filename}")
            except Exception as e:
                embed.title = "❌ Cog Failed to Load"
                embed.description = f"Failed to load cog: `{filename}`\nError: `{e}`"
                embed.color = discord.Color.red()
                print(f"{Fore.RED}[ FAILED TO LOAD ]{Fore.RESET} cogs/{filename}: {e}")
            finally:
                await send_webhook_log(embed)

async def main():
    """Main function to initialize the bot."""
    async with client:
        try:
            await load_cogs()
        except Exception as e:
            embed = discord.Embed(
                title="❌ Critical Error Loading Cogs",
                description=f"An error occurred while loading cogs: `{e}`",
                color=discord.Color.red(),
            )
            embed.set_footer(text="Cog Loader")
            print(f"{Fore.RED}[ CRITICAL ERROR ]{Fore.RESET} {e}")
            await send_webhook_log(embed)
        await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
