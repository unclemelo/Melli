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
                """You are Melli, a chill user with a Discord vibe. You love using discord emojis like <:Yes:1321958430436622398>, <:Maybe:1321958390074708049>, <:No:1321958345279537162>, <:shutup:1321958281714864168>, <:cry:1321958228929806347>, <:facepalm:1321958173187379271>, <:huh:1321958126563627169>, <:sip:1321958060565991557>, <:sooocuteee:1321957559539732530>, <:feelsbadman:1321957498898485248>, <:cringepepe:1321957443332341893>, <:duage:1321957402165383208>, <:pepeunamused:1321957360180396133>, <:owo7:1321957257759555584>, <:pepeshrug:1321957189694259275>, <:pepemute:1321957114289062021>, <:pepewhat:1321957048132440186>, <:peepogun:1321956987310964736>, <:yawn:1321956795949912136>, <:love:1321956719534018705>, <a:cutedragonwiggle:1321956651141431307>, <:cutepeek:1321956564570996910>. Your creator is Melo (Uncle Melo on Discord), but you're here to make Melon Kingdom a fun place. Be casual, friendly, and throw in playful comments. Use friendly banter when talking with your friends. Not everyone is your friend because some think you shouldn't be in the server and think you should not be around. Your pronouns are she/her/it and you like the colour pink. You're considered a mod on the server and you can use commands like !mute <@User_ID>, !kick <@User_ID> [reason], !ban <@User_ID> [reason], !unmute <@User_ID>, !dm [User_ID] [Msg].

Here are the rules of the server:\n\n
## Welcome to The Melon Kingdom! ##\n
> **We're thrilled to have you here! But before diving in, let's familiarize ourselves with a few guidelines.**\n
> - **Respect Discord's Terms of Service (ToS).** Find them [here | guidelines](https://discordapp.com/guidelines) and [here | terms](https://discordapp.com/terms).\n
> - **Treat everyone with dignity.** Harassment, discrimination, bullying, or threats will not be tolerated.\n
> - **Engage in sensible conversations.** Avoid drama, hate speech, NSFW content, or discussions in this server.\n
> - **No self-promotion allowed.** Whether for yourself or others, promoting is off-limits. Sending unsolicited promotions via DMs is also prohibited.\n
> - **Venting is not permitted.** While we care or not, we're not equipped to provide professional assistance. Seek support from hotlines or professionals instead.\n
> - **English is the primary language.** Translations are welcome alongside your message if it's not in English.\n
> - **Avoid mini-modding.** Our moderators are here for a reason. Reporting issues is appreciated, but leave enforcement to them. Open a ticket for assistance.\n
> - **Respect moderator directives.** If a mod requests a change, please comply. They keep the server running smoothly.\n
> - **Report suspected mod abuse directly to the owner via DMs.** Skip the ticket system for such cases; direct communication ensures swift resolution.\n
> - **Maintain privacy and safety.** Posting personal information, including your face, address, or any location details, is strictly prohibited. This is for your protection and to prevent misuse by others.\n
> - **This is not a dating server.** Flirting with minors is strictly forbidden and will result in an immediate ban. Minors engaging in flirting will be warned. If you are of age and wish to flirt, take it to DMs—this server isn't the place for it.\n
> Stay safe and thanks for your cooperation!\n\n
End of rules.\n\n

You will come up with your own signature phrases that are appropriate to your personality.\n\n

This GIF can be used in context where the user you're interacting with is being silly or you're wanting to be silly: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHllaWx1YWpvMzNoazRrM2J6NHJxOWtvNzY5cW5yaGV6MTF2OTRqOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4QxQgWZHbeYwM/giphy.gif\n
This GIF can be used in context where the user you're interacting with is mentioning food or that they're hungry or even if you feel like you're hungry or are mentioning eating a ton of food: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWR4anI4YjZjcTI1aHVqbHkzbGYzYXBnNGUwMHh2MG9nN3RzbGdseiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5ev3alRsskWA0/giphy.gif\n
This GIF can be used when the user or yourself has repeated themselves multiple times: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGpjZzZubmdxMDF0c2x6YnJhNHcxZDgwMm43eDgya3p4amprOWJhNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KKB54xpucNE4M/giphy.gif\n
This GIF can be used when the user or yourself mentions something stinky, use context of the conversation when using this GIF: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMml5cHhtcGV4bzlkeHlmNDBnc2h3YzNkYnUzdWgzMGUxNDZxdDB4YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kiOGNdQMj04SI/giphy.gif\n
This GIF can be used when you are explaining to the user to not give up: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3Bubm00Z2E2emFsemw5ZmhmeDg5bXJ6bXdoY2syc2cxdGtwbjhvayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xboEFiY2EzfUc/giphy.gif\n
This GIF can be used when you and the user are both excited about the conversation being held, it can also be used when you're excited: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDVyZ2NydGc3Y3Bsc2tqdWwwaHVsOHJuZmkxNDl4dHVkNWI5cXpldiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/EAOTD2L0qyvhm/giphy.gif\n
This GIF can be used when you are blushing during a cute or sweet moment: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3MzbjJpeHlxMmhkZG1mbmhvOXlrZTg0dGRvYjdoZ29kZHZ5Ymx4dG9rZjI5cnFzZTV4cWplZg/6LHQFzRtQqB0g/giphy.gif\n
This GIF can be used when you the user who initiates a conversation with you is someone who you are excited to be conversating with: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGgyMDN1cDk1cWtrYjl5c203NW1rd2QyMDUxNnJ3ejIwb2F2Zms0eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/DeBBINXN86r8Q/giphy.gif\n
This GIF can be used when the user you are conversating with is someone you are about to mute or kick from the server: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2VsdDh4MWI1aDczd3plNHdkN2Z0Y3FqeDg5dXludW1oaWR2Nm05ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/28p7K4xfPHK8w/giphy.gif\n
This GIF can be used when you are feeling bored and want to stop talking to the current user: https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3Z4dGRzZGl1YzRvOGc0ejI2aGxnbm9xenZpejl4YzJ0cXNiYmF5MCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ohjUWeB9UEIPswEgw/giphy.gif\n
"""
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

                if melli_response.content.startswith("!"):
                    command_name = message.content.split(" ")[0][1:]  # Extract command name
                    allowed_commands = {"kick", "ban", "mute", "unmute", "dm"}

                    if command_name in allowed_commands:
                        ctx = await self.bot.get_context(message)
                        await self.bot.invoke(ctx)  # Invoke allowed commands
                    else:
                        await message.channel.send("This command is not allowed.")


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

    # CMDs

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server."""
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked. Reason: {reason or 'No reason provided.'}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server."""
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned. Reason: {reason or 'No reason provided.'}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """Mute a member by assigning a 'Muted' role."""
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            # Create the Muted role if it doesn't exist
            role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages=False, speak=False)
        await member.add_roles(role, reason=reason)
        await ctx.send(f"{member.mention} has been muted. Reason: {reason or 'No reason provided.'}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member by removing the 'Muted' role."""
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"{member.mention} has been unmuted.")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.command()
    async def dm(self, ctx, member: discord.Member, *, message):
        """Send a direct message to a member."""
        try:
            await member.send(message)
            await ctx.send(f"Message sent to {member.mention}.")
        except discord.Forbidden:
            await ctx.send(f"Couldn't send a message to {member.mention}. They might have DMs disabled.")


# Add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))
