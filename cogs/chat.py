import discord
from discord.ext import commands
import openai
import json
import random
import asyncio


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

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listener for all messages in the server. Melli will decide when to respond.
        """
        # Ignore messages from the bot itself
        if message.author.bot:
            return

        # Debugging: Log received messages
        print(f"Message received: {message.content} by {message.author}")

        # Check if the message contains a keyword or Melli "feels like responding"
        if any(keyword in message.content.lower() for keyword in self.keywords) or random.random() < self.random_chance:
            # Construct the prompt
            prompt = f"""
            You are Melli, a virtual assistant created by Melo. Here is your profile:
            {json.dumps(self.melli_profile, indent=2)}

            Act accordingly to help users of Melon Kingdom Discord server.
            A user has said: "{message.content}"
            Respond as Melli in a helpful or playful way.
            """

            try:
                # Send the prompt to the OpenAI API
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are Melli, a virtual assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                melli_response = response['choices'][0]['message']['content'].strip()

                # Send Melli's response to the same channel
                await message.channel.send(melli_response)

            except Exception as e:
                # Handle errors (e.g., API errors)
                print(f"Error: {e}")

        # Pass the message to the command processor
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
                continue  # Skip if no valid channels

            channel = random.choice(available_channels)
            prompt = f"""
            You are Melli, a virtual assistant created by Melo. Here is your profile:
            {json.dumps(self.melli_profile, indent=2)}

            Say something playful or engaging to the members of the server.
            """

            try:
                # Generate a random message
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are Melli, a virtual assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                melli_response = response['choices'][0]['message']['content'].strip()

                # Send Melli's random message
                await channel.send(melli_response)

            except Exception as e:
                print(f"Error: {e}")

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
