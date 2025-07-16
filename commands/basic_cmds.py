import random

OWNER_USERNAME = "unclemel0"  # replace with your Twitch username (lowercase)
REPEAT_EVERY = 10  # number of chat messages between repeats

# Track the repeat state
brb_active = False
brb_counter = 0

def handle_command(user, message):
    global brb_active, brb_counter

    msg = message.lower()
    user_lower = user.lower()

    # Increment counter every message
    brb_counter += 1

    # --- Repeating reminder ---
    if brb_active and brb_counter >= REPEAT_EVERY:
        brb_counter = 0
        return ["🔁 | Streamer is still on a short break. Hang tight! 💺"]

    # --- Public Commands ---
    if msg.startswith("!rules"):
        return [
            "📜 | **Chat Rules**",
            "1. Be respectful 🙏",
            "2. No slurs, spam, or links 🚫",
            "3. Have fun and be kind 💬"
        ]

    elif msg.startswith("!discord"):
        return [
            "🔗 | Join our Discord! -> https://discord.gg/qHwTPewGxW"
        ]

    elif msg.startswith("!hug"):
        return [f"🤗 | @{user} sends a warm hug to everyone in chat!"]

    elif msg.startswith("!8ball"):
        responses = [
            "🎱 | Yes, definitely.",
            "🎱 | No way.",
            "🎱 | Ask again later...",
            "🎱 | It's a mystery 🕵️",
            "🎱 | Without a doubt.",
            "🎱 | Not looking good.",
        ]
        return [random.choice(responses)]

    elif msg.startswith("!flip"):
        return [f"🪙 | @{user} flips a coin... and it lands on **{random.choice(['Heads', 'Tails'])}**!"]

    elif msg.startswith("!dice"):
        roll = random.randint(1, 6)
        return [f"🎲 | @{user} rolled a **{roll}**!"]

    elif msg.startswith("!lurk"):
        return [f"👀 | @{user} is now lurking. Thanks for the support 💜"]

    elif msg.startswith("!unlurk"):
        return [f"🎉 | @{user} is back from the shadows!"]

    elif msg.startswith("!help"):
        return ["!rules, !discord, !hug, !8ball, !flip, !dice, !lurk, !unlurk"]

    # --- Owner-only Commands ---
    if user_lower == OWNER_USERNAME:
        if msg.startswith("!brb"):
            brb_active = True
            brb_counter = 0
            return ["🔕 | Streamer is taking a short break. Hang tight! 💺"]

        elif msg.startswith("!back"):
            brb_active = False
            return ["✅ | Streamer is back! Thanks for waiting 💜"]

        elif msg.startswith("!nomic"):
            return ["🎮 | Switching games, be back shortly with something new!"]

    return None
