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

def connect():
    s = socket.socket()
    s.connect((HOST, PORT))
    s.send(f"PASS {TOKEN}\r\n".encode("utf-8"))
    s.send(f"NICK {USERNAME}\r\n".encode("utf-8"))
    s.send(f"JOIN {CHANNEL}\r\n".encode("utf-8"))
    print(f"Connected to {CHANNEL} as {USERNAME}")
    return s

irc = connect()
mod = ModerationHandler(config)

def send_message(msg):
    irc.send(f"PRIVMSG {CHANNEL} :{msg}\r\n".encode("utf-8"))

def timeout(user, reason, duration=10):
    send_message(f"/timeout {user} {duration} AutoMod: {reason}")
    print(f"[TIMEOUT] {user}: {reason}")

# Track the last time a message was received
last_received_time = time.time()
TIMEOUT_THRESHOLD = 600  # 10 minutes

while True:
    try:
        resp = irc.recv(2048).decode("utf-8")
        if not resp:
            raise ConnectionResetError("No response received, reconnecting...")

        last_received_time = time.time()

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

        # Auto reconnect if idle too long
        if time.time() - last_received_time > TIMEOUT_THRESHOLD:
            print("Connection idle too long, reconnecting...")
            irc.close()
            time.sleep(2)
            irc = connect()
            last_received_time = time.time()

    except Exception as e:
        print("Error:", e)
        try:
            irc.close()
        except:
            pass
        time.sleep(5)
        irc = connect()
        last_received_time = time.time()
