import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

# Role Names
VERIFIED_ROLE_NAME = "Verified Account"
UNVERIFIED_ROLE_NAME = "Unverified Account"

# Replace this with your actual log channel ID (as an integer)
LOG_CHANNEL_ID = 123456789012345678

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ✅")
    await check_role_conflicts.start()  # Start the task to fix any role conflicts

@bot.event
async def on_member_update(before, after):
    guild = after.guild
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    
    before_roles = set(before.roles)
    after_roles = set(after.roles)

    verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)

    if not verified_role or not unverified_role:
        print("Roles not found.")
        return

    # CASE 1: Gained Verified → Remove Unverified
    if verified_role in after_roles and verified_role not in before_roles:
        if unverified_role in after_roles:
            await after.remove_roles(unverified_role, reason="User got Verified Account")
            if log_channel:
                await log_channel.send(
                    f"✅ Removed `{UNVERIFIED_ROLE_NAME}` from {after.mention} (gained `{VERIFIED_ROLE_NAME}`)"
                )

    # CASE 2: Gained Unverified → Remove Verified
    if unverified_role in after_roles and unverified_role not in before_roles:
        if verified_role in after_roles:
            await after.remove_roles(verified_role, reason="User got Unverified Account")
            if log_channel:
                await log_channel.send(
                    f"🚫 Removed `{VERIFIED_ROLE_NAME}` from {after.mention} (gained `{UNVERIFIED_ROLE_NAME}`)"
                )

# 🛠️ On-startup fix: removes unverified from users who have both roles
@tasks.loop(count=1)
async def check_role_conflicts():
    for guild in bot.guilds:
        verified = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        unverified = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
        log_channel = guild.get_channel(LOG_CHANNEL_ID)

        if not verified or not unverified:
            print(f"One or both roles not found in {guild.name}")
            continue

        for member in guild.members:
            if verified in member.roles and unverified in member.roles:
                try:
                    await member.remove_roles(unverified, reason="Conflict fix on bot startup")
                    if log_channel:
                        await log_channel.send(
                            f"🛠️ Fixed role conflict: Removed `{UNVERIFIED_ROLE_NAME}` from {member.mention} (had both)"
                        )
                except Exception as e:
                    print(f"Error fixing {member.name}: {e}")

# 🔑 Start the bot
bot.run('YOUR_BOT_TOKEN')
