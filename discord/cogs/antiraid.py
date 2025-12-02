import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

class AntiRaid(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.antiraid_enabled = {}  # guild_id: bool

    def is_admin():
        async def predicate(interaction: discord.Interaction):
            if interaction.user.guild_permissions.administrator:
                return True
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You need **Administrator** permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return app_commands.check(predicate)

    @app_commands.command(name="antiraid", description="Toggle anti-raid lockdown mode.")
    @app_commands.choices(
        state=[
            app_commands.Choice(name="On", value="on"),
            app_commands.Choice(name="Off", value="off")
        ]
    )
    @app_commands.describe(reason="Optional reason for the lockdown (only when enabling)")
    @is_admin()
    async def antiraid(self, interaction: discord.Interaction, state: app_commands.Choice[str], reason: str = None):
        guild = interaction.guild
        guild_id = guild.id

        # ===========================
        # ENABLE LOCKDOWN
        # ===========================
        if state.value == "on":
            if self.antiraid_enabled.get(guild_id, False):
                embed = discord.Embed(
                    title="⚠️ Already Enabled",
                    description="Anti-Raid Lockdown is **already active**.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            self.antiraid_enabled[guild_id] = True

            lockdown_embed = discord.Embed(
                title="⚠️ Server Lockdown",
                description="This server is currently under **anti-raid lockdown**.\n"
                            "All non-staff messages will result in an **automatic timeout**.",
                color=discord.Color.orange()
            )
            if reason:
                lockdown_embed.add_field(name="Reason", value=reason, inline=False)
            lockdown_embed.set_footer(text="Admins may still talk freely.")

            # Send lockdown message & enable slowmode
            for channel in guild.text_channels:
                try:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed=lockdown_embed)
                    if channel.permissions_for(guild.me).manage_channels:
                        await channel.edit(slowmode_delay=5)
                except Exception:
                    continue

            confirm = discord.Embed(
                title="✅ Anti-Raid Enabled",
                description="Lockdown mode has been **activated**.",
                color=discord.Color.orange()
            )
            if reason:
                confirm.add_field(name="Reason", value=reason, inline=False)
            await interaction.response.send_message(embed=confirm, ephemeral=True, delete_after=18000)

        # ===========================
        # DISABLE LOCKDOWN
        # ===========================
        elif state.value == "off":
            if not self.antiraid_enabled.get(guild_id, False):
                embed = discord.Embed(
                    title="⚠️ Already Disabled",
                    description="Anti-Raid Lockdown is **not active**.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            self.antiraid_enabled[guild_id] = False

            unlock_embed = discord.Embed(
                title="✅ Lockdown Lifted",
                description="The server lockdown has been **lifted**.\nNormal chat activity may resume.",
                color=discord.Color.green()
            )

            for channel in guild.text_channels:
                try:
                    if channel.permissions_for(guild.me).manage_channels:
                        await channel.edit(slowmode_delay=0)
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed=unlock_embed)
                except Exception:
                    continue

            confirm = discord.Embed(
                title="✅ Anti-Raid Disabled",
                description="Lockdown mode has been **deactivated**.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=confirm, ephemeral=True, delete_after=30)

    # ===========================
    # MESSAGE ENFORCEMENT
    # ===========================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        if not self.antiraid_enabled.get(guild_id, False):
            return  # Not in lockdown

        # Allow admins to bypass
        if message.author.guild_permissions.administrator:
            return

        try:
            await message.delete()
            await message.author.timeout(
                timedelta(hours=1),
                reason="Spoke during Anti-Raid lockdown."
            )

            # Optional DM notice to user
            try:
                dm_embed = discord.Embed(
                    title="🚨 Lockdown Violation",
                    description=f"You attempted to send a message in **{message.guild.name}** while the server was under lockdown.\n"
                                "You have been **timed out for 1 hour**.",
                    color=discord.Color.red()
                )
                await message.author.send(embed=dm_embed, delete_after=30)
            except Exception:
                pass

        except discord.Forbidden:
            pass  # Bot missing perms
        except Exception:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiRaid(bot))
