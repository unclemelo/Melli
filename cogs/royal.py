import discord, json, random

from discord.ext.commands import cooldown, BucketType
from datetime import timedelta
from colorama import Fore
from discord import app_commands
from discord.ext import commands


class Royal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_tree_error

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await interaction.response.send_message(f"Command is currently on cooldown! Try again in **{error.retry_after:.2f}** seconds!")
        elif isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message(f"You're missing permissions to use that")
        else:
            raise error

    
        

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded royal.py")

    
    @app_commands.command(name="kill", description="Using a weapon you can timeout a member for 30s or more")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id))
    @app_commands.choices(tool=[
        app_commands.Choice(name="Sniper", value="sniper"),
        app_commands.Choice(name="Shotgun", value="shotie"),
        ])
    async def snipecmd(self, interaction: discord.Interaction, tool: app_commands.Choice[str], member: discord.Member = None):
        # If no member is provided, pick a random member from the guild
        if member is None:
            member = random.choice(interaction.guild.members)
        
        # Make sure the member isn't the bot itself
        if member == interaction.guild.me:
            await interaction.response.send_message("I can't snipe myself!", ephemeral=True)
            return
        
        try:
            if (tool.value == 'sniper'):
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="( -_•)▄︻デ══━一 sniped")
                await interaction.response.send_message(f"( -_•)▄︻デ══━一 `{member.name}` has been sniped by `{interaction.user}`", ephemeral=False)
            elif (tool.value == 'shotie'):
                n = random.choice(["boom", "blank"])
                if n == "boom":
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=60), reason="( -_•)▄︻═════ Boom!")
                    await interaction.response.send_message(f"( -_•)▄︻═════💥 `{member.name}` has been shotguned by `{interaction.user}` with a **explosive** round", ephemeral=False)
                else:
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="( -_•)▄︻═════ Boom!")
                    await interaction.response.send_message(f"( -_•)▄︻═════ `{member.name}` has been shotguned by `{interaction.user}` with buck shot", ephemeral=False)

        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout that user.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to timeout the user.", ephemeral=True)
        
    
    

async def setup(bot: commands.Bot):
    await bot.add_cog(Royal(bot))