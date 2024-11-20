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

async def setup(bot: commands.Bot):
    await bot.add_cog(Royal(bot))
