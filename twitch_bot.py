import socket
import json
import re
import os
import time
from dotenv import load_dotenv

from moderation import ModerationHandler
from commands import basic_cmds
from send_to_discord import send_mod_alert
from twitch_queue import twitch_queue

load_dotenv()

USERNAME = os.getenv("TWITCH_USERNAME")
TOKEN = os.getenv("TWITCH_TOKEN")
CHANNEL = os.getenv("TWITCH_CHANNEL")

with open("config.json") as f:
    config = json.load(f)

HOST = "irc.chat.twitch.tv"
PORT = 6667

irc = socket.socket()
irc.connect((HOST, PORT))
irc.send(f"PASS {TOKEN}\r\n".encode("utf-8"))
irc.send(f"NICK {USERNAME}\r\n".encode("utf-8"))
irc.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))

mod = ModerationHandler(config)

def send_message(msg):
    irc.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode("utf-8"))

def timeout(user, reason, duration=10):
    send_message(f"/timeout {user} {duration} AutoMod: {reason}")
    print(f"[TIMEOUT] {user}: {reason}")

print(f"Connected to {CHANNEL} as {USERNAME}")

while True:
    try:
        resp = irc.recv(2048).decode("utf-8")

        if resp.startswith("PING"):
            irc.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            continue

        match = re.search(r":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.*)", resp)
        if match:
            user = match.group(1)
            message = match.group(2).strip()
            print(f"{user}: {message}")

            reason = mod.should_timeout(user, message)
            if reason:
                send_mod_alert(user, message, reason)
                continue

            response = basic_cmds.handle_command(user, message)
            if response:
                if isinstance(response, list):
                    for line in response:
                        send_message(line)
                        time.sleep(0.8)
                else:
                    send_message(response)

        # Check for mod queue actions from Discord
        try:
            action, user = twitch_queue.get_nowait()
            if action == "timeout":
                timeout(user, "Manually triggered from Discord")
        except:
            pass

    except Exception as e:
        print("Error:", e)
        break
