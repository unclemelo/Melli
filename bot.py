## Libraries
import discord
import os
import asyncio
import requests
from discord.ext import commands, tasks
from discord import Webhook
from dotenv import load_dotenv
from typing import Optional

## Load Environment Variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK')

## Bot Setup
intents = discord.Intents.all()
client = commands.AutoShardedBot(command_prefix="!", shard_count=1, intents=intents)
client.remove_command('help')

status_messages = [
    "🍉 | I'm a silly goober. :3",
    "🌐 | Active in {guild_count} servers!",
    "⚙️ | Type /help for commands!"
]

# ---------------------- Webhook Logger with Queue ----------------------
class WebhookLogger:
    def __init__(self, webhook_url: str, delay: float = 2.0):
        self.webhook_url = webhook_url
        self.queue = asyncio.Queue()
        self.delay = delay
        self.task = None

    def start(self):
        if not self.task:
            self.task = asyncio.create_task(self._run())

    async def _run(self):
        while True:
            embed = await self.queue.get()
            try:
                response = requests.post(
                    self.webhook_url,
                    json={"embeds": [embed.to_dict()]},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 204:
                    print(f"[WEBHOOK ERROR] {response.status_code} | {response.text}")
            except Exception as e:
                print(f"[WEBHOOK SEND FAILED] {e}")
            await asyncio.sleep(self.delay)

    async def send(self, embed: discord.Embed):
        await self.queue.put(embed)

# Instantiate the logger
logger = WebhookLogger(WEBHOOK_URL)

def build_embed(title: str, description: str, level: str = "info") -> discord.Embed:
    colors = {
        "success": discord.Color.green(),
        "error": discord.Color.red(),
        "info": discord.Color.blurple(),
        "warn": discord.Color.orange()
    }
    embed = discord.Embed(
        title=title,
        description=description,
        color=colors.get(level, discord.Color.default())
    )
    embed.set_footer(text="System Log")
    return embed

# ---------------------- Bot Events & Tasks ----------------------

@client.event
async def on_ready():
    logger.start()  # start the webhook logger
    try:
        synced = await client.tree.sync()
        await logger.send(build_embed("✅ Synced", f"{len(synced)} commands successfully synced.", "success"))
    except Exception as e:
        print(f"[SYNC FAILED] {e}")
        await logger.send(build_embed("❌ Sync Failed", f"Error: `{e}`", "error"))

    await logger.send(build_embed(
        f"<:mellilogo:1341933009359732736> {client.user.name} Online",
        f"**Logged in as:** {client.user} (`{client.user.id}`)\n"
        f"**Guilds:** {len(client.guilds)}\n"
        f"**Latency:** {round(client.latency * 1000)}ms",
        "info"
    ))

    if not update_status_loop.is_running():
        update_status_loop.start()

@tasks.loop(seconds=10)
async def update_status_loop():
    try:
        guild_count = len(client.guilds)
        latency = round(client.latency * 1000)
        latency_message = "📡 | Ping: 999+ms" if latency > 999 else f"📡 | Ping: {latency}ms"
        all_statuses = status_messages + [latency_message]
        current = all_statuses[update_status_loop.current_loop % len(all_statuses)].format(guild_count=guild_count)
        await client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.watching, name=current)
        )
    except Exception as e:
        await logger.send(build_embed("❌ Status Update Failed", f"`{e}`", "error"))

async def load_cogs():
    """Loads all cogs and sends a summary embed after all have been processed."""
    loaded = []
    failed = []

    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            name = filename[:-3]
            try:
                await client.load_extension(f'cogs.{name}')
                loaded.append(filename)
                
            except Exception as e:
                failed.append((filename, str(e)))
                

    # Build embed
    embed = discord.Embed(
        title="📦 Cog Load Summary",
        color=discord.Color.green() if not failed else discord.Color.orange()
    )
    if loaded:
        embed.add_field(
            name="✅ Successfully Loaded",
            value="\n".join(f"`{file}`" for file in loaded),
            inline=False
        )
    if failed:
        embed.color = discord.Color.red()
        embed.add_field(
            name="❌ Failed to Load",
            value="\n".join(f"`{file}` - `{error}`" for file, error in failed),
            inline=False
        )

    embed.set_footer(text="Cog Loader")
    await logger.send(embed)

async def main():
    try:
        await load_cogs()
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        await logger.send(build_embed(
            "🚨 Critical Error Loading Cogs",
            f"An unexpected error occurred while loading cogs:\n`{e}`",
            "error"
        ))

    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        await logger.send(build_embed("🛑 Shutdown", "Bot manually stopped with Ctrl+C.", "warn"))
        await client.close()  # Gracefully close connection
    except Exception as e:
        print(f"[FAILED TO START] {e}")
        await logger.send(build_embed("❌ Failed to Start Bot", f"`{e}`", "error"))


if __name__ == "__main__":
    asyncio.run(main())
