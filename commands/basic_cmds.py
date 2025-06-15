import random

def handle_command(user, message):
    msg = message.lower()

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

    return None
