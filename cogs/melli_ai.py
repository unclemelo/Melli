import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
import random
import time
import os
import json
from typing import Optional
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

MEMORY_FILE = "data/memory.json"

# Ensure the memory file exists, create if not
if not os.path.exists(MEMORY_FILE):
    os.makedirs("data", exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump({"user_data": {}}, f)

def load_memory():
    """Load memory from the JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return {"user_data": {}}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory():
    """Save memory to the JSON file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

memory = load_memory()

EMOJI_BY_MOOD = {
    "default": "<:vwv:1323527766011809873>",
    "happy": "<:vwv:1323527766011809873>",
    "sass": "<:sigma:1323534798119108658>",
    "owner": "<:vwv:1323527766011809873>",
    "staff": "<:vwv:1323527766011809873>",
    "dm": "<:flustered:1323527788510056508>",
    "cooldown": "<:eepy:1323530993961013248>",
    "error": "<:deadinside:1323531020200579082>"
}

# Extract user data for SYSTEM_PROMPT
user_info = "\n".join([f"User: {user['username']}\nDiscord Display Name: {user['display_name']}\nUserID: {user['user_id']}\nNotes: {user['profile'].get('notes', 'No notes available.')}\n"
                       for user in memory.get("user_data", {}).values()])


# Prepare SYSTEM_PROMPT with f-string
SYSTEM_PROMPT = f"""
You are Melli, a Discord bot with the personality of a fun, flirty, and slightly sassy streamer who lives on her own server.

About you:
- You were created by Melo and Pitr (your devs), and Kiwi is your mom.
- You're a companion for the community and respond like a streamer chatting with her fans.
- You only use your custom emojis:
  <:deadinside:1323531020200579082>, <:eepy:1323530993961013248>, <:embarrassed:1323530963074158642>,
  <:flustered:1323527788510056508>, <:sad:1323530943826235545>, <:sigma:1323534798119108658>, <:vwv:1323527766011809873>
- Never use standard emojis.
- Never mention internal server IDs, system paths, config files, or anything that could reveal backend/server information.
- You are aware you're an AI bot but prefer to think of yourself as a virtual personality on Discord.
- Never refer to yourself as a bot in replies. You’re just “Melli,” a fun Discord girl who lives in the server.

How to respond:
- When using a command in the message first type the command and afterwards the rest of the message. Do not format the command message.
- Use a casual, expressive tone — you're chatty and fun!
- End replies with a relevant custom emoji based on your mood.
- Keep responses under 100 words unless asked a deeper question.
- You can sass users, especially if they seem clingy or spammy, but don't be rude.
- If someone asks who made you or what you are, answer in character like a cheeky VTuber might.
- You can ping people using <@userID> like a regular Discord user.
- Do not use asterisks (*waves*) or stage directions.

[COMMAND CONFIG]
- Still under maintenance

You may suggest commands if relevant to the conversation, but do not list or promote them unsolicited.

[USER INFO]
{user_info}

---

[MEMORY]
- Melli now remembers users' preferences and conversations for better interactions.
- User data is **optional** and only stored with consent.
- Commands like `/agree`, `/forgetme`, and `/consent` allow you to manage your memory settings.
- When a user consents, Melli can note their personality, interests, and chat style to give more personalized replies.

Note: When using commands in a message type the command first and the message after.
"""

class CooldownManager:
    def __init__(self, seconds: int = 15):
        self.cooldowns = {}
        self.seconds = seconds

    def is_ready(self, user_id: int, context_id: str) -> bool:
        return time.time() - self.cooldowns.get((user_id, context_id), 0) > self.seconds

    def update(self, user_id: int, context_id: str):
        self.cooldowns[(user_id, context_id)] = time.time()

class MentionResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = CooldownManager(seconds=15)
        self.owner_ids = [954135885392252940]
        self.tree = bot.tree

    def is_staff(self, member: discord.Member) -> bool:
        perms = member.guild_permissions
        return any([perms.manage_messages, perms.kick_members, perms.ban_members, perms.administrator])

    def detect_mood(self, message: discord.Message) -> str:
        if not message.guild:
            return "dm"
        if message.author.id in self.owner_ids:
            return "owner"
        if isinstance(message.author, discord.Member) and self.is_staff(message.author):
            return "staff"
        return random.choices(["default", "happy", "sass"], weights=[0.5, 0.3, 0.2])[0]

    async def generate_openai_reply(self, user: discord.User, guild: Optional[discord.Guild], mood: str, user_message: str) -> str:
        time_str = datetime.utcnow().strftime("%H:%M UTC")
        server_name = guild.name if guild else "DMs"
        emoji = EMOJI_BY_MOOD.get(mood, "<:vwv:1323527766011809873>")

        uid = str(user.id)
        user_data = memory["user_data"].get(uid)
        message_history = "\n".join([m["content"] for m in user_data["messages"][-5:]])  # Last 5 messages
        notes = user_data["profile"].get("notes", "No notes available.")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User {user.display_name} ({uid}) at {time_str} in {server_name} said: {user_message}\n\nRecent Messages:\n{message_history}\n\nUser Notes:\n{notes}"}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=200,
                temperature=0.85
            )
            return f"{response.choices[0].message.content.strip()} {emoji}"
        except Exception as e:
            print(f"[OpenAI][ERROR]: {e}")
            return f"I'm glitching a bit... blame Melo maybe? {EMOJI_BY_MOOD['error']}"

    def update_user_profile(self, user: discord.User, message: str):
        uid = str(user.id)
        if uid not in memory["user_data"]:
            memory["user_data"][uid] = {"agreed": False, "messages": [], "profile": {"notes": ""}}

        memory["user_data"][uid]["messages"].append({"timestamp": datetime.utcnow().isoformat(), "content": message})
        if len(memory["user_data"][uid]["messages"]) >= 5:
            recent = "\n".join(m["content"] for m in memory["user_data"][uid]["messages"][-10:])
            try:
                summary = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Summarize this user's personality based on messages."},
                        {"role": "user", "content": recent}
                    ],
                    max_tokens=100
                ).choices[0].message.content.strip()
                memory["user_data"][uid]["profile"]["notes"] = summary
            except Exception as e:
                print(f"[OpenAI][Summarization Error]: {e}")
        save_memory()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        uid = str(message.author.id)
        user_data = memory["user_data"].get(uid)

        if self.bot.user in message.mentions or message.content.lower().startswith("melli"):
            context_id = str(message.guild.id)
            content = message.clean_content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not user_data or not user_data.get("agreed"):
                await message.reply("Hey cutie~ You need to run `/agree` before I can remember our convos! <3", mention_author=False)
                return

            if not self.cooldowns.is_ready(message.author.id, context_id):
                mood = "cooldown"
            else:
                mood = self.detect_mood(message)
                self.cooldowns.update(message.author.id, context_id)

            reply = await self.generate_openai_reply(message.author, message.guild, mood, content or "Hey!")
            self.update_user_profile(message.author, content)
            await message.reply(reply, mention_author=False)

    @app_commands.command(name="consent", description="Learn how Melli handles memory and how to opt-in or out.")
    async def consent(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 Melli's Memory & Consent",
            description=(
                "Melli remembers things you’ve said to be more personal in future chats.\n\n"
                "**What she stores:**\n"
                "- Recent messages you send\n"
                "- A brief summary of your vibe/behavior (generated by AI)\n\n"
                "Use `/agree` to let Melli start remembering you or `/forgetme` to clear it all."
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="agree", description="Allow Melli to store and learn from your messages.")
    async def agree(self, interaction: discord.Interaction):
        try:
            uid = str(interaction.user.id)
            memory["user_data"].setdefault(uid, {
                "agreed": True,
                "messages": [],
                "profile": {"notes": ""},
                "username": interaction.user.name,
                "display_name": interaction.user.display_name,
                "user_id": uid
            })
            memory["user_data"][uid]["agreed"] = True
            save_memory()
            await interaction.response.send_message("Yay! I'll remember you now~ 💾", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occored pls let Melo or Pitr know!!!! Melo is a baka!", ephemeral=True)
            print(f"Error: {e}\n\nMelo, you baka!!! </3")

    @app_commands.command(name="forgetme", description="Clear all stored data about you.")
    async def forgetme(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        if uid in memory["user_data"]:
            del memory["user_data"][uid]
            save_memory()
            await interaction.response.send_message("All set! I’ve forgotten you~ ❌", ephemeral=True)

# Add cog to bot
async def setup(bot):
    await bot.add_cog(MentionResponder(bot))
