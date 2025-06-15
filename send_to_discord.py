import requests
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_mod_alert(user, message, reason):
    if not DISCORD_WEBHOOK_URL:
        print("[!] No webhook set")
        return

    data = {
        "embeds": [{
            "title": "🚨 Potential Violation Detected",
            "color": 0xFF0000,
            "fields": [
                {"name": "User", "value": f"`{user}`", "inline": True},
                {"name": "Reason", "value": reason, "inline": True},
                {"name": "Message", "value": message, "inline": False}
            ],
            "footer": {
                "text": "Click below to open Twitch"
            },
            "url": "https://www.twitch.tv/uncle_melo_"
        }],
        "content": "## **[🔗 Open Twitch](https://www.twitch.tv/uncle_melo_)** ##"
    }


    requests.post(DISCORD_WEBHOOK_URL, json=data)
