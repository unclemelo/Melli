import discord
from discord.ext import commands
from openai import OpenAI
import json
import random
import asyncio
import aiohttp  # For sending webhook messages

client = OpenAI(api_key='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')

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_id = 954135885392252940  # Creator/Father ID
        self.memory = {}  # Simple memory storage

        # Load Melli's profile
        with open('data/melli_profile.json', 'r') as file:
            self.melli_profile = json.load(file)

        self.task_started = False

    def update_memory(self, user_id, data):
        """Update memory for a specific user."""
        if user_id not in self.memory:
            self.memory[user_id] = {}
        self.memory[user_id].update(data)

    def get_memory(self, user_id):
        """Retrieve memory for a specific user."""
        return self.memory.get(user_id, {})

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener for messages Melli should respond to."""
        if message.author.bot:
            return

        if any(keyword in message.content.lower() for keyword in ["hello", "melli", "help"]) or random.random() < 0.2:
            prompt = (
                f"You are Melli, a chill assistant. Respond to the message casually, "
                f"keeping it short and fun. You never use emojis and should respond naturally. "
                f"Message: {message.content}"
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": "You are a playful and chill assistant named Melli."},
                              {"role": "user", "content": prompt}],
                    max_tokens=50,
                )
                melli_response = response.choices[0].message.content.strip()
                # Store conversation in memory
                self.update_memory(message.author.id, {"last_message": message.content, "response": melli_response})
                await message.channel.send(melli_response)
            except Exception as e:
                error_message = f"Error responding to message '{message.content}' by {message.author}: {e}"
                print(error_message)
                await self.send_error_webhook(error_message)

        await self.bot.process_commands(message)

    async def random_message_task(self):
        """Melli occasionally sends random, relaxed messages."""
        while True:
            await asyncio.sleep(random.randint(300, 900))  # Wait 5–15 mins
            available_channels = [
                channel for guild in self.bot.guilds for channel in guild.text_channels
                if channel.permissions_for(guild.me).send_messages
            ]
            if not available_channels:
                continue

            channel = random.choice(available_channels)
            prompt = (
                f"You are Melli, a playful assistant. Say something fun, casual, or engaging, "
                f"without using emojis. Make it sound natural."
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": "You are a fun and casual assistant named Melli."},
                              {"role": "user", "content": prompt}],
                    max_tokens=50,
                )
                melli_response = response.choices[0].message.content.strip()
                await channel.send(melli_response)
            except Exception as e:
                error_message = f"Error sending random message: {e}"
                print(error_message)
                await self.send_error_webhook(error_message)

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts Melli's random message task."""
        if not self.task_started:
            self.bot.loop.create_task(self.random_message_task())
            self.task_started = True

    async def send_error_webhook(self, error_message: str):
        """Send error message to a specified webhook."""
        async with aiohttp.ClientSession() as session:
            try:
                payload = {"content": f"⚠️ **Melli Error:** {error_message}"}
                async with session.post(self.error_webhook_url, json=payload) as response:
                    if response.status != 204:
                        print(f"Failed to send webhook: {response.status} {await response.text()}")
            except Exception as e:
                print(f"Failed to send error webhook: {e}")

# Add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))
