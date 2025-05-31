# Melli

**Melli** is now public! Built with community management in mind, Melli enhances moderation, automation, and engagement in your Discord server. This README will guide you through setting up and running the bot locally.

---

## 🚀 Features & Commands

### 🛡️ AutoMod Tools
- `/setup` — Launch an interactive AutoMod configuration wizard.  
- `/forceupdate` — Instantly refresh AutoMod rules.  
- `/show_config` — View your current AutoMod settings in a neat embed.  
- `/clear_config` — Reset all AutoMod settings for your server.  
- `/set_log_channel <channel>` — Set a temporary log channel manually.

### 🔨 Moderation Tools
- `/mute <user> <duration> [reason]` — Temporarily mute a user.  
- `/unmute <user>` — Remove a timeout from a user.  
- `/clear <amount>` — Bulk delete messages.  
- `/warn <user> <reason>` — Warn a user.  
- `/warnings <user>` — Show a user's warning history.  
- `/delwarn <warning_id>` — Delete a specific warning.  
- `/clearwarns <user>` — Remove all warnings from a user.  
- `/kick <user> [reason]` — Kick a member from the server.  
- `/ban <user> [reason]` — Ban a member from the server.  
- `/unban <user>` — Unban a previously banned user.

### ⚙️ Utility Commands
- `/supporters` — View top boosters of the support server.  
- `/profile [user]` — View your or another user's profile.  
- `/add_melli` — Invite Melli to your server and see project credits.  
- `/config` — Toggle command availability per server.

### 🔊 Voice Channel Tools
- `/bump <user> <target_vc>` — Move a user to another voice channel.  
- `/vc_mute <user>` — Server mute a user in voice chat.  
- `/vc_unmute <user>` — Unmute a user in voice chat.  
- `/deafen <user>` — Server deafen a user.  
- `/undeafen <user>` — Remove deafening from a user.  
- `/kickvc <user>` — Disconnect a user from a voice channel.

### 🎉 Fun & Extra Commands
- `/knockout <user>` — Timeout a user dramatically.  
- `/revive <user>` — Bring a timed-out user back.  
- `/prank <user>` — Harmlessly prank a user.  
- `/chaos` — Temporarily unleash controlled chaos.

---

## 🧰 Prerequisites

Before you begin, make sure the following are installed:

1. **Python 3.11+**  
2. **pip** (Python package manager)  
3. **Git** (optional but recommended)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/unclemelo/Melli
cd Melli
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Linux/Mac
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

> 💡 *If any dependencies are outdated or cause issues, feel free to open an issue.*

---

## ⚙️ Configuration

### 1. Create a `.env` File

In the project root, create a `.env` file and add:

```env
TOKEN=your_discord_bot_token
WEBHOOK=your_webhook_url
```

- Replace `your_discord_bot_token` with your bot token from the [Discord Developer Portal](https://discord.com/developers/docs/intro).
- Replace `your_webhook_url` with your Discord webhook URL (optional, for logging or console output).

### 2. Set Up the Database

Ensure the following files exist in the `data/` directory:

- `warns.json`
- `user_stats.json`
- `memory.json`
- `guildConf.json`
- `bot_stats.json`
- `applied_presets.json`

> If missing, Melli may auto-generate them on first launch. If not, create empty JSON files to prevent errors.

---

## ▶️ Running the Bot

To start the bot:

```bash
# On Windows
python bot.py

# On Linux/Mac
python3 bot.py
```

> ✅ The bot should now start and connect to your Discord server. Check your terminal for confirmation or errors.

---

## 📁 Folder Structure

```
Melli/
├── cogs/               # Modular bot features
├── data/               # Bot data and configuration files
├── .env.example        # Example .env configuration
├── requirements.txt    # Python dependencies
├── LICENSE             # Project license
└── README.md           # You're here!
```

---

## ❗ Troubleshooting

1. **Bot token error**  
   - Double-check the `TOKEN` value in your `.env` file.

2. **Missing dependencies**  
   - Run `pip install -r requirements.txt` again.

3. **Missing data files**  
   - Make sure all required JSON files in the `data/` folder exist and are valid.

---

## 🤝 Contributing

Contributions are welcome! If you help improve Melli's codebase, your Discord ID will be added to the bot's badge system as a contributor.

Feel free to open issues, submit pull requests, or suggest new features!

---

*Let us know if you need help setting up or want to expand Melli’s features. We're always happy to collaborate!*