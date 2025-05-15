import discord, json, random
import asyncio
from discord.ext.commands import cooldown, BucketType
from datetime import timedelta
from discord import app_commands
from discord.ext import commands
from util.command_checks import command_enabled
from util.booster_cooldown import BoosterCooldownManager

cooldown_manager_user = BoosterCooldownManager(rate=1, per=600, bucket_type="user")
cooldown_manager_guild = BoosterCooldownManager(rate=1, per=600, bucket_type="guild")

class Royal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="knockout", description="Use a weapon to timeout a member for 30 seconds or more!")
    @app_commands.choices(tool=[
        app_commands.Choice(name="Sniper", value="sniper"),
        app_commands.Choice(name="Shotgun", value="shotie"),
        app_commands.Choice(name="Pistol", value="pistol"),
        app_commands.Choice(name="Grenade", value="grenade"),
        app_commands.Choice(name="Rocket Launcher", value="rocket"),
        app_commands.Choice(name="Club", value="club"),
    ])
    @command_enabled()
    async def knockoutcmd(self, interaction: discord.Interaction, tool: app_commands.Choice[str], member: discord.Member = None):
        remaining = await cooldown_manager_user.get_remaining(interaction)
        if remaining > 0:
            await interaction.response.send_message(
                f"You're on cooldown! Try again in {round(remaining, 1)}s.", ephemeral=True
            )
            return

        await cooldown_manager_user.trigger(interaction)

        # If no member is provided, pick a random member from the guild
        if member is None:
            member = random.choice(interaction.guild.members)

        # Ensure the bot cannot target itself
        if member == interaction.guild.me:
            await interaction.response.send_message("I can't target myself!", ephemeral=True)
            return
        elif member == interaction.user:
                embed = discord.Embed(
                    title="Help is Available",
                    description="- Speak with someone today\n`988` Suicide and Crisis Lifeline",
                    color=discord.Color.red()  # You can customize the color
                )
                embed.add_field(name="Languages", value="*English, Spanish*", inline=False)
                embed.add_field(name="Hours", value="Available 24 hours", inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return


        try:
            embed = discord.Embed(color=discord.Color.red())

            if tool.value == 'sniper':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="( -_•)▄︻デ══━一 Sniped")
                embed.title = "🔫 Sniper Shot!"
                embed.description = f"( -_•)▄︻デ══━一 {member.mention} has been **sniped** by {interaction.user.mention}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790458889146398/sinon-sao.gif?ex=673f3999&is=673de819&hm=c0eec9ad754ebe2be6b970944255ca951e3099e562b400e5e7cea5fd1443956c&")  # Replace with an image URL

            elif tool.value == 'shotie':
                outcome = random.choice(["explosive", "buckshot"])
                if outcome == "explosive":
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=60), reason="Explosive round!")
                    embed.title = "💥 Explosive Shotgun Blast!"
                    embed.description = f"{member.mention} was hit with an **explosive round** by {interaction.user.mention}!"
                else:
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="Buckshot!")
                    embed.title = "🔫 Buckshot Blast!"
                    embed.description = f"{member.mention} was peppered with **buckshot** by {interaction.user.mention}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790449795895347/shotgun-bread-boys.gif?ex=673f3997&is=673de817&hm=9d44ec914cc4136fd465eb058644e4e790623e94fae18363af718e2677aced6e&")  # Replace with an image URL

            elif tool.value == 'pistol':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=20), reason="Quick shot!")
                embed.title = "🔫 Pistol Shot!"
                embed.description = f"{member.mention} was swiftly shot by {interaction.user.mention}! Precision at its finest."
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790414626656256/gun-fire.gif?ex=673f398e&is=673de80e&hm=fbbedb181d2798f5cc8d5f7aeea49fa62b456b38c403e40f95600dbfabc5cebc&")

            elif tool.value == 'grenade':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=90), reason="BOOM! Grenade explosion!")
                embed.title = "💣 Grenade Explosion!"
                embed.description = f"{member.mention} was caught in a **grenade explosion** launched by {interaction.user.mention}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790148493873162/boom.gif?ex=673f394f&is=673de7cf&hm=db599e2dc587b30174c498d444a3aa5f4b45dc057379cf2b81d16ba43c78e0fc&")

            elif tool.value == 'rocket':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=120), reason="Direct hit from a rocket!")
                embed.title = "🚀 Rocket Launcher!"
                embed.description = f"{member.mention} was obliterated by a **rocket launcher** wielded by {interaction.user.mention}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308789861880299583/laser-eye.gif?ex=673f390b&is=673de78b&hm=677edca23d9011967c5054703709e1c5101b038ea7e65d9d8ecdc2fe4d47be8d&")

            elif tool.value == 'club':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=15), reason="quick little bonk")
                embed.title = ":hammer: Get bonked out of here!"
                embed.description = f"{member.mention} was obliterated by a **hammer** wielded by {interaction.user.mention}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1290652330127003679/1326216909854736515/bonk-anime.gif?ex=677e9f3f&is=677d4dbf&hm=e1bf477e25d8c947b31b37fc8cb52d234a5393875f58b345feb1600b2e7b9aae&")

            # Add a footer to the embed
            embed.set_footer(text="Cooldown: 10 minutes")
            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout that user.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to timeout the user.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Royal(bot))