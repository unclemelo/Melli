import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_FILE = "data/guildConf.json"

class MigrationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return {"Servers": {}}
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_config(self, config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    """@app_commands.command(name="migrate_config", description="Migrate config to include all commands by default")
    @app_commands.checks.has_permissions(administrator=True)
    async def migrate_config(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        config = self.load_config()
        updated = False
        for guild_id, guild_conf in config.get("Servers", {}).items():
            guild_conf.setdefault("DevOnly", {})
            guild_conf.setdefault("UnderMaintenance", {})
            for cmd in self.bot.tree.get_commands():
                if (cmd.name not in guild_conf and
                    cmd.name not in guild_conf["DevOnly"] and
                    cmd.name not in guild_conf["UnderMaintenance"]):
                    guild_conf[cmd.name] = True
                    updated = True

        if updated:
            self.save_config(config)
            await interaction.followup.send("✅ Config migrated and updated!", ephemeral=True)
        else:
            await interaction.followup.send("No updates needed, config already up-to-date.", ephemeral=True)"""

async def setup(bot):
    await bot.add_cog(MigrationCog(bot))
