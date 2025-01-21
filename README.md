# Melli

**Melli** is a private Discord bot built for managing and enhancing the experience of your community. This README provides step-by-step instructions to set up and run the bot locally.

---

## Features

- **Automod**: Automatically moderates chat messages based on customizable rules. (Melli Devs Only | No release yet)
- **Error Handling**: Graceful handling of errors to ensure a seamless experience.
- **Custom Commands**: Miscellaneous commands for fun and utility.
- **Royal System**: Special module for unique server mechanics.

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Python 3.11+**
2. **pip** (Python package manager)
3. **Git** (optional, but recommended for cloning this repository)

---

## Installation

Follow these steps to set up and run the bot:

 ### 1. Clone the Repository

```bash
git clone https://github.com/unclemelo/Melli
cd Melli
```

 ### 2. Set Up a Virtual Environment (Recommended)

Create a virtual environment to isolate dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

 ### 3. Install Dependencies (Sumbit an issue if outdated libs)

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## Configuration

 ### 1. Create a .env File

The `.env` file holds sensitive information such as your bot token. Create it in the project root if it doesn't already exist and add the following:

```env
TOKEN=your_discord_bot_token
WEBHOOK=your_webhook_url
```

Replace your_discord_bot_token with your actual Discord bot token. (You can get this from the [Discord Developer Portal](https://discord.com/developers/docs/intro).)
Replace your_webhook_url with your actual Discord webhook url.

### 2. Set Up the Database

Ensure the `data/warns.json`, `data/config.json`, and `AM_conf.json` files exists. If it's missing, you may need to generate it or let the bot handle database creation on first launch (if supported).
---

## Running the Bot

To run the bot:

```bash
python bot.py # On Windows
python3 bot.py # On Linux/Mac
```

*The bot should now start and connect to your Discord server. Check the console output for any errors or confirmation that the bot is online.*

---

## Folder Structure

- `cogs/`: Contains the bot's modular features (e.g., automod, custom commands, royal system).
- `data/`: Stores bot data like databases and configuration files.
- `.env.example`: Example .env file for configuration.
- `requirements.txt`: Lists Python dependencies.
- `LICENSE`: License file for the project.
- `README.md`: This documentation file.

---

## Troubleshooting

1. Bot Token Error: Ensure the correct token is in the `.env` file.

2. Missing Dependencies: Run `pip install -r requirements.txt` again.

3. Database Issues: Verify the `data/warns.json`, `data/config.json`, and `AM_conf.json` files exists and is properly configured.

---

## Contributing

This bot is private for now, but contributions may be considered in the future. Reach out to the maintainer for more details.

---

*Let me know if you'd like help improving or adding functionality!*

