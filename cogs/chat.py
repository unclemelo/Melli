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

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listener for all messages in the server. Melli will decide when to respond.
        """
        # Ignore messages from the bot itself
        if message.author.bot:
            return

        # Check if the message contains a keyword or Melli "feels like responding"
        if any(keyword in message.content.lower() for keyword in self.keywords) or random.random() < self.random_chance:
            # Construct the prompt
            prompt = f"""
            You are Melli, a virtual assistant created by Melo. Here is your profile:
            {json.dumps(self.melli_profile, indent=2)}

            Act accordingly to help users of Kofinisu's Cafe Discord server.
            A user has said: "{message.content}"
            Respond as Melli in a helpful or playful way.
            """

            try:
                # Send the prompt to the OpenAI API
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=150
                )
                melli_response = response.choices[0].text.strip()

                # Send Melli's response to the same channel
                await message.channel.send(melli_response)

            except Exception as e:
                # Handle errors (e.g., API errors)
                print(f"Error: {e}")

    async def random_message_task(self):
        """
        Melli occasionally sends random messages to keep the chat lively.
        """
        while True:
            await asyncio.sleep(random.randint(300, 900))  # Wait 5 to 15 minutes
            channel = random.choice(self.bot.guilds[0].text_channels)  # Choose a random channel
            prompt = f"""
            You are Melli, a virtual assistant created by Melo. Here is your profile:
            {json.dumps(self.melli_profile, indent=2)}

            Say something playful or engaging to the members of the server.
            """

            try:
                # Generate a random message
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=150
                )
                melli_response = response.choices[0].text.strip()

                # Send Melli's random message
                await channel.send(melli_response)

            except Exception as e:
                print(f"Error: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Start Melli's random message task when the bot is ready.
        """
        self.bot.loop.create_task(self.random_message_task())

# Add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))
