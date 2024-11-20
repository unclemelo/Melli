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

    
    @app_commands.command(name="kill", description="Use a weapon to timeout a member for 30 seconds or more!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id))
    @app_commands.choices(tool=[
        app_commands.Choice(name="Sniper", value="sniper"),
        app_commands.Choice(name="Shotgun", value="shotie"),
        app_commands.Choice(name="Pistol", value="pistol"),
        app_commands.Choice(name="Grenade", value="grenade"),
        app_commands.Choice(name="Rocket Launcher", value="rocket"),
    ])
    async def snipecmd(self, interaction: discord.Interaction, tool: app_commands.Choice[str], member: discord.Member = None):
        # If no member is provided, pick a random member from the guild
        if member is None:
            member = random.choice(interaction.guild.members)

        # Ensure the bot cannot target itself
        if member == interaction.guild.me:
            await interaction.response.send_message("I can't target myself!", ephemeral=True)
            return

        try:
            embed = discord.Embed(color=discord.Color.red())

            if tool.value == 'sniper':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="( -_•)▄︻デ══━一 Sniped")
                embed.title = "🔫 Sniper Shot!"
                embed.description = f"( -_•)▄︻デ══━一 `{member.name}` has been **sniped** by `{interaction.user.display_name}`!"
                embed.set_image(url="https://tenor.com/view/sinon-sao-sword-art-online-gif-25208771")  # Replace with an image URL

            elif tool.value == 'shotie':
                outcome = random.choice(["explosive", "buckshot"])
                if outcome == "explosive":
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=60), reason="Explosive round!")
                    embed.title = "💥 Explosive Shotgun Blast!"
                    embed.description = f"`{member.name}` was hit with an **explosive round** by `{interaction.user.display_name}`!"
                else:
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="Buckshot!")
                    embed.title = "🔫 Buckshot Blast!"
                    embed.description = f"`{member.name}` was peppered with **buckshot** by `{interaction.user.display_name}`!"
                embed.set_image(url="https://tenor.com/view/shotgun-bread-boys-gif-22775719")  # Replace with an image URL

            elif tool.value == 'pistol':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=20), reason="Quick shot!")
                embed.title = "🔫 Pistol Shot!"
                embed.description = f"`{member.name}` was swiftly shot by `{interaction.user.display_name}`! Precision at its finest."
                embed.set_image(url="https://tenor.com/view/gun-fire-anime-shoot-blam-gif-5256396")

            elif tool.value == 'grenade':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=90), reason="BOOM! Grenade explosion!")
                embed.title = "💣 Grenade Explosion!"
                embed.description = f"`{member.name}` was caught in a **grenade explosion** launched by `{interaction.user.display_name}`!"
                embed.set_image(url="https://tenor.com/view/boom-gif-20562682")  # Replace with an image URL

            elif tool.value == 'rocket':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=120), reason="Direct hit from a rocket!")
                embed.title = "🚀 Rocket Launcher!"
                embed.description = f"`{member.name}` was obliterated by a **rocket launcher** wielded by `{interaction.user.display_name}`!"
                embed.set_image(url="https://tenor.com/view/laser-eye-rocket-launcher-missile-gif-20287288")  # Replace with an image URL

            # Add a footer to the embed
            embed.set_footer(text="Cooldown: 10 minutes")
            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout that user.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to timeout the user.", ephemeral=True)

        
    
    

async def setup(bot: commands.Bot):
    await bot.add_cog(Royal(bot))