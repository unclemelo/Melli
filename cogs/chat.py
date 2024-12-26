import discord
from discord.ext import commands
from openai import OpenAI

client = OpenAI(api_key='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')
import json
import random
import asyncio
import aiohttp  # For sending webhook messages


class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load Melli's profile
        with open('data/melli_profile.json', 'r') as file:
            self.melli_profile = json.load(file)

        # Emojis for Melli to use
        self.emojis = ["😊", "😜", "✨", "😎", "👍", "🎉", "🥳", "💖", "<:custom_emoji:1234567890>"]
        self.task_started = False

    def pick_random_emoji(self):
        """Selects a random emoji from the emoji list with a certain probability."""
        if random.random() < 0.3:  # 30% chance to include an emoji
            return random.choice(self.emojis)
        return ""  # No emoji

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener for messages Melli should respond to."""
        if message.author.bot:
            return

        if any(keyword in message.content.lower() for keyword in ["hello", "melli", "help"]) or random.random() < 0.2:
            prompt = (
                f"You are Melli, a chill virtual assistant. Respond to the message casually, "
                f"keeping it short and fun. Sometimes, you can use emojis like {random.choice(self.emojis)} if it feels right.\n\n"
                f"Message: {message.content}"
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a playful and chill assistant named Melli."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=50,
                )
                melli_response = response.choices[0].message.content.strip()
                emoji = self.pick_random_emoji()
                if emoji:
                    melli_response += f" {emoji}"  # Append the emoji if chosen
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
                f"and maybe use an emoji if it feels natural."
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a fun and casual assistant named Melli."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=50,
                )
                melli_response = response.choices[0].message.content.strip()
                emoji = self.pick_random_emoji()
                if emoji:
                    melli_response += f" {emoji}"  # Append the emoji if chosen
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


async def setup(bot: commands.Bot):
    """Add the ChatCog to the bot."""
    await bot.add_cog(ChatCog(bot))