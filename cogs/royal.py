import discord, json, random
import asyncio
from discord.ext.commands import cooldown, BucketType
from datetime import timedelta
from colorama import Fore
from discord import app_commands
from discord.ext import commands

class Royal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_tree_error
        self.stats_file = "data/weapon_stats.json"
        self.image_urls = {
            "sniper": "https://cdn.discordapp.com/attachments/1183985896039661658/1308790458889146398/sinon-sao.gif",
            "shotie_explosive": "https://cdn.discordapp.com/attachments/1183985896039661658/1308790449795895347/shotgun-bread-boys.gif",
            "pistol": "https://cdn.discordapp.com/attachments/1183985896039661658/1308790414626656256/gun-fire.gif",
            "grenade": "https://cdn.discordapp.com/attachments/1183985896039661658/1308790148493873162/boom.gif",
            "rocket": "https://cdn.discordapp.com/attachments/1183985896039661658/1308789861880299583/laser-eye.gif",
        }
        self.dud_probabilities = {
            "sniper": 0.1,  # 10% chance of being a dud
            "shotie": 0.15,  # 15% chance
            "pistol": 0.05,  # 5% chance
            "grenade": 0.2,  # 20% chance
            "rocket": 0.25,  # 25% chance
        }
        self.load_stats()

    def load_stats(self):
        try:
            with open(self.stats_file, "r") as file:
                self.weapon_stats = json.load(file)
        except FileNotFoundError:
            self.weapon_stats = {tool: 0 for tool in ["sniper", "shotie", "pistol", "grenade", "rocket"]}
    
    def save_stats(self):
        with open(self.stats_file, "w") as file:
            json.dump(self.weapon_stats, file, indent=4)

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        print(f"on_tree_error triggered with error: {type(error).__name__}")
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"Take a chill pill! Command is cooling off. Try again in **{error.retry_after:.2f}** seconds.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "LOL, you thought? Not enough perms, buddy.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(f"{error}")
            print(f"An error occurred: {error}")
            raise error


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded royal.py - Time to wreak havoc!")

    @app_commands.command(name="knockout", description="Use a weapon to timeout a member for 30 seconds or more!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    @app_commands.choices(tool=[
        app_commands.Choice(name="Sniper", value="sniper"),
        app_commands.Choice(name="Shotgun", value="shotie"),
        app_commands.Choice(name="Pistol", value="pistol"),
        app_commands.Choice(name="Grenade", value="grenade"),
        app_commands.Choice(name="Rocket Launcher", value="rocket"),
    ])
    async def knockoutcmd(self, interaction: discord.Interaction, tool: app_commands.Choice[str], member: discord.Member = None):
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
                embed.description = f"( -_•)▄︻デ══━一 {member.name} has been **sniped** by {interaction.user.display_name}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790458889146398/sinon-sao.gif?ex=673f3999&is=673de819&hm=c0eec9ad754ebe2be6b970944255ca951e3099e562b400e5e7cea5fd1443956c&")  # Replace with an image URL

            elif tool.value == 'shotie':
                outcome = random.choice(["explosive", "buckshot"])
                if outcome == "explosive":
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=60), reason="Explosive round!")
                    embed.title = "💥 Explosive Shotgun Blast!"
                    embed.description = f"{member.name} was hit with an **explosive round** by {interaction.user.display_name}!"
                else:
                    await member.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="Buckshot!")
                    embed.title = "🔫 Buckshot Blast!"
                    embed.description = f"{member.name} was peppered with **buckshot** by {interaction.user.display_name}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790449795895347/shotgun-bread-boys.gif?ex=673f3997&is=673de817&hm=9d44ec914cc4136fd465eb058644e4e790623e94fae18363af718e2677aced6e&")  # Replace with an image URL

            elif tool.value == 'pistol':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=20), reason="Quick shot!")
                embed.title = "🔫 Pistol Shot!"
                embed.description = f"{member.name} was swiftly shot by {interaction.user.display_name}! Precision at its finest."
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790414626656256/gun-fire.gif?ex=673f398e&is=673de80e&hm=fbbedb181d2798f5cc8d5f7aeea49fa62b456b38c403e40f95600dbfabc5cebc&")

            elif tool.value == 'grenade':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=90), reason="BOOM! Grenade explosion!")
                embed.title = "💣 Grenade Explosion!"
                embed.description = f"{member.name} was caught in a **grenade explosion** launched by {interaction.user.display_name}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308790148493873162/boom.gif?ex=673f394f&is=673de7cf&hm=db599e2dc587b30174c498d444a3aa5f4b45dc057379cf2b81d16ba43c78e0fc&")  # Replace with an image URL

            elif tool.value == 'rocket':
                await member.timeout(discord.utils.utcnow() + timedelta(seconds=120), reason="Direct hit from a rocket!")
                embed.title = "🚀 Rocket Launcher!"
                embed.description = f"{member.name} was obliterated by a **rocket launcher** wielded by {interaction.user.display_name}!"
                embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308789861880299583/laser-eye.gif?ex=673f390b&is=673de78b&hm=677edca23d9011967c5054703709e1c5101b038ea7e65d9d8ecdc2fe4d47be8d&")  # Replace with an image URL

            # Add a footer to the embed
            embed.set_footer(text="Cooldown: 10 minutes")
            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout that user.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to timeout the user.", ephemeral=True)


    

    @app_commands.command(name="revive", description="Bring back a timed-out user with flair!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def revive_cmd(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(timed_out_until=None)
            embed = discord.Embed(
                title="✨ Resurrection Complete!",
                description=f"`{member.name}` has been revived by `{interaction.user.display_name}`! Hopefully, they behave this time. 🤞",
                color=discord.Color.green()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1183985896039661658/1308808048030126162/love-live-static.gif?ex=673f49fb&is=673df87b&hm=e53b7c74842f2939f60c71bdad015a1013b28c0476f41244e8a8091464143f02&")
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to revive them. RIP again. 😔", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Failed to revive. The afterlife is holding onto them tight.", ephemeral=True)
        except Exception as e:
            print(f"Error: {e}")


    @app_commands.command(name="chaos", description="Unleash chaos on the server (temporarily).")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def chaos_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            members = interaction.guild.members
            skipped_members = []  # Track members that couldn't be edited

            for member in random.sample(members, min(len(members), 10)):
                try:
                    random_nickname = f"💥 {random.choice(['Goblin', 'Legend', 'Potato', 'Dud'])}"
                    await member.edit(nick=random_nickname)
                except discord.Forbidden:
                    skipped_members.append(member)
                except discord.HTTPException:
                    continue  # Ignore and move to the next member

            chaos_message = "Chaos unleashed! Check those nicknames. 😈"
            if skipped_members:
                chaos_message += f"\n\nCouldn't touch {len(skipped_members)} members. They're either protected or untouchable. 😏"

            await interaction.followup.send(chaos_message)

            # Reset the chaos after some time
            await asyncio.sleep(60)
            for member in members:
                try:
                    await member.edit(nick=None)
                except (discord.Forbidden, discord.HTTPException):
                    continue  # Skip members we can't reset

            await interaction.followup.send("Chaos reverted. Everyone’s back to normal. For now.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            await interaction.followup.send("Something went wrong during chaos mode. Abort!", ephemeral=True)


    @app_commands.command(name="prank", description="Play a harmless prank on a member!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    async def prank_cmd(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        prank_nick = f"{member.name} 🤡"
        try:
            await member.edit(nick=prank_nick)
            await interaction.followup.send(f"`{member.name}` is now known as `{prank_nick}`. Let the giggles begin!")
            await asyncio.sleep(60)
            await member.edit(nick=None)
            await interaction.followup.send("Prank over. Nickname restored!")
        except discord.Forbidden:
            await interaction.followup.send("I can't prank them. They're protected by Discord gods. 🙄", ephemeral=True)
        except Exception as e:
            print(f"Error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Royal(bot))
