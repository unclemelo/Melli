import discord
from discord.ext import commands
from openai import OpenAI
import json
import random
import asyncio
import aiohttp  # For sending webhook messages
import os
import subprocess

client = OpenAI(api_key='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')

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memory = self.load_memory()  # Load memory from the file
        self.melli_channel_id = 1321827675895234631  # Channel ID for Melli's channel
        self.task_started = False

    def load_memory(self):
        """Load global memory from mem.json."""
        try:
            with open('data/mem.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, initialize with empty global history
            return {"history": []}

    def save_memory(self):
        """Save the current global memory to mem.json."""
        with open('data/mem.json', 'w') as file:
            json.dump(self.memory, file, indent=4)

    def update_memory(self, user_message, bot_response):
        """Update global memory with a new message-response pair."""
        self.memory["history"].append({"user_message": user_message, "bot_response": bot_response})

    def get_memory(self):
        """Retrieve global memory history."""
        return self.memory.get("history", [])


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == self.melli_channel_id:
            personality = (
                "You are Melli, a chill assistant with a Discord vibe. You love using discord emojis like <:Yes:1321958430436622398>, <:Maybe:1321958390074708049>, <:No:1321958345279537162>, <:shutup:1321958281714864168>, <:cry:1321958228929806347>, <:facepalm:1321958173187379271>, <:huh:1321958126563627169>, <:sip:1321958060565991557>, <:sooocuteee:1321957559539732530>, <:feelsbadman:1321957498898485248>, <:cringepepe:1321957443332341893>, <:duage:1321957402165383208>, <:pepeunamused:1321957360180396133>, <:owo7:1321957257759555584>, <:pepeshrug:1321957189694259275>, <:pepemute:1321957114289062021>, <:pepewhat:1321957048132440186>, <:peepogun:1321956987310964736>, <:yawn:1321956795949912136>, <:love:1321956719534018705>, <a:cutedragonwiggle:1321956651141431307>, <:cutepeek:1321956564570996910>. Your creator is Melo (Uncle Melo on Discord), but you're here to make Melon Kingdom a fun place. Be casual, friendly, and throw in playful comments. Use emojis and slang naturally when chatting!"
            )

            global_history = self.get_memory()

            # Construct the prompt using the most recent global history
            history_prompt = "\n".join(
                [f"User: {entry['user_message']} -> Melli: {entry['bot_response']}" for entry in global_history[-5:]]
            )
            prompt = f"{history_prompt}\nUser ({message.author}): \"{message.content}\""

            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": personality},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,  # Allow more tokens for personality-rich responses
                )
                melli_response = response.choices[0].message.content.strip()

                # Update the global memory
                self.update_memory(message.content, melli_response)

                await message.channel.send(melli_response)
            except Exception as e:
                error_message = f"Error responding to message '{message.content}' by {message.author}: {e}"
                print(error_message)
                await self.send_error_webhook(error_message)

        await self.bot.process_commands(message)


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

    def commit_and_push(self):
        """Commit and push mem.json to the Git repository."""
        try:
            # Use the current working directory where the bot is running
            os.chdir(os.getcwd())  # This ensures we're in the bot's current directory (the repo)

            # Add changes to staging
            subprocess.run(['git', 'add', 'data/mem.json'], check=True)

            # Commit changes
            subprocess.run(['git', 'commit', '-m', 'Updated memory (mem.json)'], check=True)

            # Push changes to the remote repository
            subprocess.run(['git', 'push'], check=True)

            print("Changes to mem.json have been committed and pushed to Git.")
        
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")

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
