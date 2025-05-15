import json
import os
import discord
from functools import wraps

CONFIG_FILE = "data/guildConf.json"

# -------------------------------
# Core Configuration I/O
# -------------------------------

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

def ensure_guild_config_structure(config: dict) -> dict:
    """Ensures all guilds have DevOnly and UnderMaintenance keys."""
    for guild_id, guild_conf in config["Servers"].items():
        guild_conf.setdefault("DevOnly", {})
        guild_conf.setdefault("UnderMaintenance", {})
    return config

# -------------------------------
# Guild Config Accessors
# -------------------------------

def get_guild_config(guild_id: int):
    """Returns the guild's command settings, initializes if missing."""
    config = load_config()
    config = ensure_guild_config_structure(config)

    if str(guild_id) not in config["Servers"]:
        config["Servers"][str(guild_id)] = {"DevOnly": {}, "UnderMaintenance": {}}
        save_config(config)

    return config["Servers"][str(guild_id)]

def is_command_enabled(guild_id: int, command_name: str) -> bool:
    """Checks if a command is enabled for the guild."""
    guild_config = get_guild_config(guild_id)
    if command_name in guild_config.get("UnderMaintenance", {}):
        return False
    return guild_config.get(command_name, True)

def toggle_command(guild_id: int, command_name: str, value: bool, category: str = "General"):
    """Enables or disables a command for the server with category handling."""
    config = load_config()
    config = ensure_guild_config_structure(config)

    if str(guild_id) not in config["Servers"]:
        config["Servers"][str(guild_id)] = {"DevOnly": {}, "UnderMaintenance": {}}

    if category == "DevOnly":
        config["Servers"][str(guild_id)]["DevOnly"][command_name] = value
    elif category == "UnderMaintenance":
        config["Servers"][str(guild_id)]["UnderMaintenance"][command_name] = value
    else:
        config["Servers"][str(guild_id)][command_name] = value

    save_config(config)

def update_commands_for_guild(bot: discord.Client, guild_id: int):
    """Syncs the command tree with the server's settings."""
    config = load_config()
    config = ensure_guild_config_structure(config)
    guild_config = get_guild_config(guild_id)

    for cmd in bot.tree.get_commands():
        if not is_command_enabled(guild_id, cmd.name):
            bot.tree.remove_command(cmd.name)
        else:
            if cmd.name not in [command.name for command in bot.tree.commands]:
                bot.tree.add_command(cmd)

    bot.tree.sync(guild=discord.Object(id=guild_id))

# -------------------------------
# Decorators
# -------------------------------

def command_enabled():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if interaction.guild_id is None:
                return await interaction.response.send_message(
                    "This command can only be used in a server.", ephemeral=True
                )
            if not is_command_enabled(interaction.guild_id, func.__name__):
                return await interaction.response.send_message(
                    "❌ This command is disabled in this server.", ephemeral=True
                )
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def dev_only_command():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            config = get_guild_config(interaction.guild_id)
            if not config.get("DevOnly", {}).get(func.__name__, False):
                return await interaction.response.send_message(
                    "🚫 This command is restricted to bot developers.", ephemeral=True
                )
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def maintenance_mode():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            config = get_guild_config(interaction.guild_id)
            if config.get("UnderMaintenance", {}).get(func.__name__, False):
                return await interaction.response.send_message(
                    "🛠 This command is currently under maintenance.", ephemeral=True
                )
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def role_required(role_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if not interaction.guild or not interaction.user:
                return await interaction.response.send_message(
                    "This command must be used in a server.", ephemeral=True
                )

            member = interaction.guild.get_member(interaction.user.id)
            if not member:
                return await interaction.response.send_message("Member not found.", ephemeral=True)

            if not any(role.name == role_name for role in member.roles):
                return await interaction.response.send_message(
                    f"❌ You need the `{role_name}` role to use this command.", ephemeral=True
                )

            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator
