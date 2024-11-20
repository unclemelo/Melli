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
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Take a chill pill! Command is cooling off. Try again in **{error.retry_after:.2f}** seconds.", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("LOL, you thought? Not enough perms, buddy.", ephemeral=True)
        else:
            print(f"An error occurred: {error}")
            raise error

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[ OK ]{Fore.RESET} Loaded royal.py - Time to wreak havoc!")

    @app_commands.command(name="help_kill", description="Learn how to obliterate your friends (virtually).")
    async def helpkill_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Royal Commands", color=discord.Color.blurple())
        embed.add_field(name="/kill", value="Pick a weapon and show them who's boss.", inline=False)
        embed.add_field(name="Cooldown", value="Every weapon needs a 10-minute breather after unleashing chaos.", inline=False)
        embed.add_field(name="Duds", value="Sometimes your weapon decides to nap instead. Deal with it.", inline=False)
        embed.set_footer(text="Command responsibly... or not.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kill", description="Time to choose violence. Use a weapon to timeout someone!")
    @app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id, i.guild.id))
    @app_commands.choices(tool=[
        app_commands.Choice(name="Sniper", value="sniper"),
        app_commands.Choice(name="Shotgun", value="shotie"),
        app_commands.Choice(name="Pistol", value="pistol"),
        app_commands.Choice(name="Grenade", value="grenade"),
        app_commands.Choice(name="Rocket Launcher", value="rocket"),
    ])
    async def snipecmd(self, interaction: discord.Interaction, tool: app_commands.Choice[str], member: discord.Member = None):
        member = member or random.choice(interaction.guild.members)
        if member == interaction.guild.me:
            await interaction.response.send_message("You really wanna try me? Nope, not happening.", ephemeral=True)
            return

        try:
            if random.random() < self.dud_probabilities[tool.value]:
                await interaction.response.send_message(f"Oops! Your **{tool.name}** went full potato mode. Better luck next time.", ephemeral=False)
                return

            embed = discord.Embed(color=discord.Color.red())
            timeout_durations = {"sniper": 30, "shotie": 60, "pistol": 20, "grenade": 90, "rocket": 120}
            duration = timeout_durations[tool.value]
            
            if tool.value == "shotie":
                outcome = random.choice(["explosive", "buckshot"])
                tool_key = "shotie_explosive" if outcome == "explosive" else "shotie"
                embed.title = "💥 Explosive Shotgun Boom!" if outcome == "explosive" else "🔫 Buckshot Mayhem!"
                embed.description = f"`{member.name}` got absolutely wrecked by `{interaction.user.display_name}` with an **{outcome} round**!"
            else:
                tool_key = tool.value
                embed.title = f"🚀 {tool.name.capitalize()} Attack!"
                embed.description = f"`{member.name}` just got vaporized by `{interaction.user.display_name}`. Rest in pepperonis."
            
            await member.timeout(discord.utils.utcnow() + timedelta(seconds=duration), reason=f"Hit with a {tool.name}")
            embed.set_image(url=self.image_urls.get(tool_key, ""))
            embed.set_footer(text=f"Cooldown: 10 minutes | Timeout Duration: {duration} seconds")
            self.weapon_stats[tool.value] += 1
            self.save_stats()
            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("Can't touch that user. Too powerful, maybe?", ephemeral=True)
        except discord.HTTPException as e:
            print(f"HTTPException: {e}")
            await interaction.response.send_message("Something broke. It wasn't me, I swear!", ephemeral=True)

    

    @app_commands.command(name="revive", description="Bring back a timed-out user with flair!")
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


    @app_commands.command(name="chaos", description="Unleash chaos on the server (temporarily).")
    async def chaos_cmd(self, interaction: discord.Interaction):
        try:
            members = interaction.guild.members
            for member in random.sample(members, min(len(members), 10)):
                random_nickname = f"💥 {random.choice(['Goblin', 'Legend', 'Potato', 'Dud'])}"
                await member.edit(nick=random_nickname)
            await interaction.response.send_message("Chaos unleashed! Check those nicknames. 😈")
            
            # Reset the chaos after some time
            await asyncio.sleep(60)
            for member in members:
                await member.edit(nick=None)
            await interaction.followup.send("Chaos reverted. Everyone’s back to normal. For now.")
        except discord.Forbidden:
            await interaction.response.send_message("I couldn't touch someone's nickname. They're protected. 😅", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Something went wrong during chaos mode. Abort!", ephemeral=True)

    @app_commands.command(name="betray", description="Sometimes, karma strikes back.")
    async def betray_cmd(self, interaction: discord.Interaction, tool: app_commands.Choice[str]):
        if random.random() < 0.2:  # 20% chance of betrayal
            embed = discord.Embed(
                title="🔄 Backfire!",
                description=f"`{interaction.user.display_name}` tried to attack but ended up timing *themselves* out! Karma's a bummer. 🤷",
                color=discord.Color.red()
            )
            await interaction.user.timeout(discord.utils.utcnow() + timedelta(seconds=30), reason="Betrayed by their own weapon")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No betrayal this time... but watch your back. 👀")

    @app_commands.command(name="prank", description="Play a harmless prank on a member!")
    async def prank_cmd(self, interaction: discord.Interaction, member: discord.Member):
        prank_nick = f"{member.name} 🤡"
        try:
            await member.edit(nick=prank_nick)
            await interaction.response.send_message(f"`{member.name}` is now known as `{prank_nick}`. Let the giggles begin!")
            await asyncio.sleep(60)
            await member.edit(nick=None)
            await interaction.followup.send("Prank over. Nickname restored!")
        except discord.Forbidden:
            await interaction.response.send_message("I can't prank them. They're protected by Discord gods. 🙄", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Royal(bot))
