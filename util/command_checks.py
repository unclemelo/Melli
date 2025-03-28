import json
import os
import discord

CONFIG_FILE = "data/guildConf.json"

def load_config():
    """Loads or creates the guildConf.json file."""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"Servers": {}}, f, indent=4)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    """Saves the current config to the file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_guild_config(guild_id: int):
    """Returns the guild's command settings, initializes if missing."""
    config = load_config()
    if str(guild_id) not in config["Servers"]:
        config["Servers"][str(guild_id)] = {}
        save_config(config)
    return config["Servers"][str(guild_id)]

def is_command_enabled(guild_id: int, command_name: str) -> bool:
    """Checks if a command is enabled for the guild."""
    guild_config = get_guild_config(guild_id)
    return guild_config.get(command_name, True)  # Default to enabled if not specified

def toggle_command(guild_id: int, command_name: str, value: bool):
    """Enables or disables a command for the server."""
    config = load_config()
    if str(guild_id) not in config["Servers"]:
        config["Servers"][str(guild_id)] = {}
    config["Servers"][str(guild_id)][command_name] = value
    save_config(config)

def update_commands_for_guild(bot: discord.Client, guild_id: int):
    """Syncs the command tree with the server's settings."""
    config = load_config()
    guild_config = get_guild_config(guild_id)

    for cmd in bot.tree.get_commands():
        if not is_command_enabled(guild_id, cmd.name):
            bot.tree.remove_command(cmd.name)
        else:
            if cmd.name not in [command.name for command in bot.tree.commands]:
                bot.tree.add_command(cmd)

    bot.tree.sync(guild=discord.Object(id=guild_id))
