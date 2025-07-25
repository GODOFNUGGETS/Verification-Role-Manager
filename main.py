import discord
from discord.ext import commands
from discord import Embed
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
VERIFIED_ROLE_NAME = os.getenv("VERIFIED_ROLE_NAME", "Verified Account")
UNVERIFIED_ROLE_NAME = os.getenv("UNVERIFIED_ROLE_NAME", "Unverified Account")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    guild = after.guild
    verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
    log_channel = guild.get_channel(LOG_CHANNEL_ID)

    if not verified_role or not unverified_role:
        print("⚠️ One or both roles not found.")
        return

    if verified_role in after.roles and verified_role not in before.roles:
        if unverified_role in after.roles:
            try:
                await after.remove_roles(unverified_role, reason="User verified")
                print(f"🔁 {after.name} was verified. Unverified role removed.")

                if log_channel:
                    embed = Embed(
                        title="User Verified",
                        description=f"{after.mention} has been verified.",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Removed Role", value=UNVERIFIED_ROLE_NAME)
                    await log_channel.send(embed=embed)
            except discord.Forbidden:
                print(f"🚫 Missing permissions for {after.name}.")
            except Exception as e:
                print(f"⚠️ Error: {e}")

bot.run(TOKEN)
