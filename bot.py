## Libraries
import discord
import os
import asyncio
import requests
from discord.ext import commands, tasks
from discord import Webhook
from dotenv import load_dotenv

## Load Environment Variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK')

## Bot Setup
intents = discord.Intents.all()
client = discord.ext.commands.AutoShardedBot(command_prefix="!", shard_count=2, intents=intents)
client.remove_command('help')

status_messages = [
    "🍉 | I'm a silly goober. :3",
    "🌐 | Active in {guild_count} servers!",
    "⚙️ | Type /help for commands!"
]

@client.event
async def on_ready():
    """Triggered when the bot is ready."""
    # Sync commands
    try:
        synced_commands = await client.tree.sync()
        print(f"+ [ SYNCED ] {len(synced_commands)} commands successfully.")
    except Exception as e:
        print(f"- [ SYNC FAILED ] {e}")

    print(f"+ [ CONNECTED ] {client.user.name} is online and ready!")
    print(f"Currently in {len(client.guilds)} guilds.")

    # Start the status update loop
    if not update_status_loop.is_running():
        update_status_loop.start()

@tasks.loop(seconds=10)
async def update_status_loop():
    """Updates the bot's presence with a rotating status every 10 seconds."""
    try:
        # Static data
        guild_count = len(client.guilds)
        latency = round(client.latency * 1000)  # Convert latency to ms

        # Status messages with system stats
        dynamic_statuses = [
            f"📡 | Ping: {latency}ms",
        ]

        # Combine static and dynamic statuses
        all_status_messages = status_messages + dynamic_statuses

        # Cycle through messages
        current_message = all_status_messages[update_status_loop.current_loop % len(all_status_messages)].format(guild_count=guild_count)
        await client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.watching, name=current_message)
        )
    except Exception as e:
        print(f"[ ERROR ] Could not update presence: {e}")

def send_webhook_log(embed: discord.Embed):
    """Sends an embed message to the specified webhook."""
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "embeds": [embed.to_dict()]  # Convert the embed to a dictionary format that Discord's API expects
    }

    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)

    if response.status_code != 204:
        print(f"Failed to send webhook. Status code: {response.status_code}, Response: {response.text}")
    else:
        pass

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
            except Exception as e:
                embed.title = "❌ Cog Failed to Load"
                embed.description = f"Failed to load cog: `{filename}`\nError: `{e}`"
                embed.color = discord.Color.red()
                print(f"[ FAILED TO LOAD ] cogs/{filename}: {e}")
            finally:
                send_webhook_log(embed)  # We no longer need async for this

async def main():
    """Main function to initialize the bot."""
    try:
        await load_cogs()
    except Exception as e:
        embed = discord.Embed(
            title="❌ Critical Error Loading Cogs",
            description=f"An error occurred while loading cogs: `{e}`",
            color=discord.Color.red(),
        )
        embed.set_footer(text="Cog Loader")
        print(f"- [ CRITICAL ERROR ] {e}")
        send_webhook_log(embed)

    await client.start(TOKEN)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
