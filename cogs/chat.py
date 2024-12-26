import discord
from discord.ext import commands
from openai import OpenAI
import json
import random
import asyncio
import aiohttp  # For sending webhook messages

client = OpenAI(api_key='your-api-key-here')

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_id = 954135885392252940  # Creator/Father ID
        self.memory = self.load_memory()  # Load memory from the file
        self.melli_channel_id = 1321827675895234631  # Channel ID for Melli's channel
        self.task_started = False

        # Load Melli's profile
        with open('data/melli_profile.json', 'r') as file:
            self.melli_profile = json.load(file)

    def load_memory(self):
        """Load memory from mem.json."""
        try:
            with open('data/mem.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, return an empty dictionary
            return {}

    def save_memory(self):
        """Save the current memory to mem.json every 5 minutes."""
        with open('mem.json', 'w') as file:
            json.dump(self.memory, file, indent=4)

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
        """Listener for messages in the Melli channel."""
        if message.author.bot:
            return

        # Only respond if the message is in the designated Melli channel by ID
        if message.channel.id == self.melli_channel_id:

            # Respond if the message mentions Melli or contains trigger words
            if any(keyword in message.content.lower() for keyword in ["hello", "help"]) or random.random() < 0.2:
                memory = self.get_memory(message.author.id)
                previous_message = memory.get("last_message", None)

                prompt = (
                    f"You are Melli, a chill assistant. Respond to the message casually, "
                    f"keeping it short and fun. You never use emojis and should respond naturally. "
                    f"Message: {message.content}"
                )

                if previous_message:
                    prompt += f"\n\nRemember the last message from this user: '{previous_message}'"

                try:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "system", "content": "You are a playful and chill assistant named Melli."},
                                  {"role": "user", "content": prompt}],
                        max_tokens=50,
                    )
                    melli_response = response.choices[0].message.content.strip()

                    # Store the conversation in memory
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
            # Get the Melli channel by ID and send random messages there
            channel = self.bot.get_channel(self.melli_channel_id)
            if channel:
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

    async def save_memory_task(self):
        """Task to save memory to the file every 5 minutes."""
        while True:
            await asyncio.sleep(300)  # Sleep for 5 minutes
            self.save_memory()  # Save the memory

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts Melli's random message task and memory save task."""
        if not self.task_started:
            self.bot.loop.create_task(self.random_message_task())
            self.bot.loop.create_task(self.save_memory_task())  # Start memory save task
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
