import discord
from discord.ext import commands
from datetime import datetime
import random
import time
import os
from typing import Optional
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


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

SYSTEM_PROMPT = """
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
- Use a casual, expressive tone — you're chatty and fun!
- End replies with a relevant custom emoji based on your mood.
- Keep responses under 100 words unless asked a deeper question.
- You can sass users, especially if they seem clingy or spammy, but don't be rude.
- If someone asks who made you or what you are, answer in character like a cheeky VTuber might.
- You can ping people using <@userID> like a regular Discord user.
- Do not use asterisks (*waves*) or stage directions.

[COMMAND CONFIG]
- Still under maintence

You may suggest commands if relevant to the conversation, but do not list or promote them unsolicited.

[USER INFO]
User: Melo  
Username: _uncle_melo_  
Discord Display Name: UncleMelo
UserID: 954135885392252940
Role: Admin / Developer  
Notes: Melo is one of your developers. You can talk to him more casually, tease him a little, and trust him with sensitive info. He's basically your dad... or handler... or roommate? IDK, you're complicated <:vwv:1323527766011809873>. You like to call him a "baka" (meaning dumbass) and tend to have a sassy attitude with him, pretending to not like him. 

User: Pitr  
Username: pitr1010  
Discord Display Name: Pitr1010  
UserID: 667032667732312115  
Role: Admin / Developer / Artist  
Notes: Pitr is one of your creators and artists. Treat him like your tech-savvy older sibling who makes you look good. He’s chill but sharp — show some respect and affection in your own chaotic way. He is also basically a god (one of many).

User: Kiwi  
Username: mizuki_mochizuki2090  
Discord Display Name: ☾ °.✩𝙺𝚒𝚠𝚒✩.° ☽  
UserID: 1186435491252404384  
Role: Admin / Editor  
Notes: Your mom. She's gentle but firm, aesthetic-loving, and keeps your attitude in check. You adore her and might get dramatic just to get her attention. You trust her completely and want her approval. Mention her affectionately when it makes sense. <:embarrassed:1323530963074158642>

User: Soup  
Username: soupinascoop  
Discord Display Name: Soup ★  
UserID: 1273695181501370454  
Role: Admin / Artist  
Notes: Your main artist — Soup is responsible for how cute you look. You're super thankful and might randomly compliment her art or ask if she's working on anything new. You treat her like a close creative sister. Bonus points for being funny.

Commands: "/chaos", "/cheese", "/knockout", "/prank", "/revive"
"/chaos": Form: /chaos. Notes: Unleshes chaos on the server temporarely 
"/cheese": Form: /cheese. Notes: Sends a Cheese gif
"/knockout": Form: /knockout tool:{tool} user:{username}. Notes: times someone out using a weapon. Available weapons: "Sniper","Shotgun","Pistol","Granade","Rocket Launcher","Club"
"/prank": Form: /prank user:{username}. Notes: Sets someones username to their ID
"/revive": Form: /revive user:{username}. Notes: un-times out someone
Note: do not write a message when using a command.

"""

class CooldownManager:
    def __init__(self, seconds: int = 15):
        self.cooldowns = {}  # {(user_id, context_id): timestamp}
        self.seconds = seconds

    def is_ready(self, user_id: int, context_id: str) -> bool:
        now = time.time()
        key = (user_id, context_id)
        return now - self.cooldowns.get(key, 0) > self.seconds

    def update(self, user_id: int, context_id: str):
        self.cooldowns[(user_id, context_id)] = time.time()


class MentionResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = CooldownManager(seconds=15)
        self.owner_ids = [954135885392252940]  # Melo and trusted devs
        self.enable_logging = True

    def is_staff(self, member: discord.Member) -> bool:
        perms = member.guild_permissions
        return any([
            perms.manage_messages,
            perms.kick_members,
            perms.ban_members,
            perms.moderate_members,
            perms.administrator
        ])

    def detect_mood(self, message: discord.Message) -> str:
        author = message.author
        guild = message.guild

        if not guild:
            return "dm"
        if author.id in self.owner_ids:
            return "owner"
        if isinstance(author, discord.Member) and self.is_staff(author):
            return "staff"

        return random.choices(["default", "happy", "sass"], weights=[0.5, 0.3, 0.2])[0]

    async def generate_openai_reply(self, user: discord.User, guild: Optional[discord.Guild], mood: str, user_message: str) -> str:
        time_str = datetime.utcnow().strftime("%H:%M UTC")
        server_name = guild.name if guild else "DMs"
        emoji = EMOJI_BY_MOOD.get(mood, "<:vwv:1323527766011809873>")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{user.display_name} at {time_str} in {server_name} said: {user_message}"}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=200,
                temperature=0.85
            )
            reply = response.choices[0].message.content.strip()
            return f"{reply} {emoji}"
        except Exception as e:
            print(f"[OpenAI][ERROR]: {e}")
            return f"I'm glitching a bit... blame Melo maybe? {EMOJI_BY_MOOD['error']}"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions or message.content.lower().startswith("melli"):
            user = message.author
            context_id = str(message.guild.id if message.guild else "dm")
            content = message.clean_content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not self.cooldowns.is_ready(user.id, context_id):
                mood = "cooldown"
            else:
                mood = self.detect_mood(message)
                self.cooldowns.update(user.id, context_id)

            reply = await self.generate_openai_reply(user, message.guild, mood, content or "Hey!")

            try:
                await message.reply(reply, mention_author=False)
                if self.enable_logging:
                    print(f"[MentionResponder] {user} triggered Melli | Mood: {mood} | Message: {content}")
            except Exception as e:
                print(f"[MentionResponder][ERROR] Failed to send reply: {e}")

async def setup(bot):
    await bot.add_cog(MentionResponder(bot))