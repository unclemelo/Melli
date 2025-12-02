import discord
from discord import app_commands
from discord.ext import commands
from util.command_checks import command_enabled  # optional if used in your bot

class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rules", description="View Melo's Melon Farm community rules.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def rules(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Welcome to Melo's Melon Farm!",
            description=(
                "> **We're thrilled to have you here! Before diving in, please take a moment to review our community guidelines.**"
            ),
            color=discord.Color.teal()
        )

        embed.add_field(
            name="📜 Discord Policy",
            value=(
                "> **Respect Discord's Terms of Service and Community Guidelines**  \n"
                "> [Terms of Service](https://discord.com/terms) | [Community Guidelines](https://discord.com/guidelines)"
            ),
            inline=False
        )

        embed.add_field(
            name="🧭 Moderation & Behavior",
            value=(
                "> **Treat everyone with respect**  \n"
                "> Harassment, discrimination, bullying, or threats will not be tolerated.\n\n"
                "> **Follow moderator instructions**  \n"
                "> If a moderator asks you to stop or adjust something, please comply.\n\n"
                "> **Avoid mini-modding**  \n"
                "> Report issues instead of trying to enforce the rules yourself — that's our job!"
            ),
            inline=False
        )

        embed.add_field(
            name="💬 Language & Conduct",
            value=(
                "> **Keep conversations sensible**  \n"
                "> No drama, hate speech, NSFW content, or inappropriate topics.\n\n"
                "> **English is the primary language**  \n"
                "> You may include translations alongside English messages if needed."
            ),
            inline=False
        )

        embed.add_field(
            name="📣 Promotion & Activity",
            value=(
                "> **No self-promotion or advertising**  \n"
                "> Don't promote your content, servers, or DMs without permission.\n\n"
                "> **Keep the vibes clean**  \n"
                "> Avoid spam, chain messages, or disruptive behavior that derails the chat."
            ),
            inline=False
        )

        embed.add_field(
            name="❤️ Safety & Privacy",
            value=(
                "> **Protect your privacy**  \n"
                "> Don't share your personal info, address, or face. Keep yourself safe online.\n\n"
                "> **No venting**  \n"
                "> We're not equipped for crisis help. Please reach out to professionals or hotlines.\n\n"
                "> **Report mod abuse directly to the owner**  \n"
                "> DM the owner privately for fast resolution — skip tickets for this."
            ),
            inline=False
        )

        embed.add_field(
            name="🚫 Dating & Boundaries",
            value=(
                "> **This is not a dating server**  \n"
                "> Flirting with minors = instant ban. Minors flirting get warned. "
                "If you're of age, take romance to DMs privately and respectfully."
            ),
            inline=False
        )

        embed.add_field(
            name="🪶 Final Note",
            value=(
                "> Rules may be updated over time — stay informed!\n"
                "> Breaking them may result in **warnings, mutes, kicks, or bans**, "
                "depending on severity.\n"
                "<@&1292648739093217290> are here to help keep things peaceful 💙"
            ),
            inline=False
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1322404741174792192/1323293231479521290/catcomputerpfp.jpg")
        embed.set_footer(text="Stay kind, stay chill — enjoy your stay at Melo's Melon Farm 🌊")

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rules(bot))
