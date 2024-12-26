import discord
from discord.ext import commands
import openai
import json
import random
import asyncio
import aiohttp  # For sending webhook messages


class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load Melli's profile from a JSON file
        with open('data/melli_profile.json', 'r') as file:
            self.melli_profile = json.load(file)

        # Set your OpenAI API key
        openai.api_key = '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'

        # Random message triggers (can be adjusted)
        self.keywords = ["hello", "melli", "help", "chat", "bot"]
        self.random_chance = 0.1  # 10% chance for Melli to respond randomly
        self.task_started = False  # Ensure the random message task runs only once
        self.error_webhook_url = (
            "https://discord.com/api/webhooks/1316466233574690917/LOdp5lcTuOWN0k6yeaRwXUPDw5AgRsz0a9FP-KRLx2kXJhfM30ei_zt2JMpO0lYN5lpN"
        )

    async def send_error_webhook(self, error_message: str):
        """
        Sends an error message to the specified webhook URL.
        """
        async with aiohttp.ClientSession() as session:
            try:
                payload = {"content": f"⚠️ **Melli Error:** {error_message}"}
                async with session.post(self.error_webhook_url, json=payload) as response:
                    if response.status != 204:
                        print(f"Failed to send webhook: {response.status} {await response.text()}")
            except Exception as e:
                print(f"Failed to send error webhook: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listener for all messages in the server. Melli will decide when to respond.
        """
        if message.author.bot:
            return

        # Debugging: Log received messages
        print(f"Message received: {message.content} by {message.author}")

        if any(keyword in message.content.lower() for keyword in self.keywords) or random.random() < self.random_chance:
            prompt = f"""
            You are Melli, a virtual assistant created by Melo. Here is your profile:
            {json.dumps(self.melli_profile, indent=2)}

            Act accordingly to help users of Melon Kingdom Discord server.
            A user has said: "{message.content}"
            Respond as Melli in a helpful or playful way.
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are Melli, a virtual assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                melli_response = response['choices'][0]['message']['content'].strip()
                await message.channel.send(melli_response)

            except Exception as e:
                error_message = f"Error responding to message '{message.content}' by {message.author}: {e}"
                print(error_message)
                await self.send_error_webhook(error_message)

        await self.bot.process_commands(message)

    async def random_message_task(self):
        """
        Melli occasionally sends random messages to keep the chat lively.
        """
        while True:
            await asyncio.sleep(random.randint(300, 900))  # Wait 5 to 15 minutes
            available_channels = [
                channel for guild in self.bot.guilds for channel in guild.text_channels
                if channel.permissions_for(guild.me).send_messages
            ]
            if not available_channels:
                continue

            channel = random.choice(available_channels)
            prompt = f"""
            You are Melli, a virtual assistant created by Melo. Here is your profile:
            {json.dumps(self.melli_profile, indent=2)}

            Say something playful or engaging to the members of the server.
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are Melli, a virtual assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                melli_response = response['choices'][0]['message']['content'].strip()
                await channel.send(melli_response)

            except Exception as e:
                error_message = f"Error sending random message: {e}"
                print(error_message)
                await self.send_error_webhook(error_message)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Start Melli's random message task when the bot is ready.
        """
        if not self.task_started:
            self.bot.loop.create_task(self.random_message_task())
            self.task_started = True


# Add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))
