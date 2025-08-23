import discord
from discord.ext import commands
from discord_slash import SlashCommand
from datetime import datetime, timedelta
import operator
import os
import json
from dotenv import load_dotenv
import sqlite3

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = commands.Bot(command_prefix=None, intents=intents)
slash = SlashCommand(client)

# Load locales
def load_locale(lang=None):
    if not lang:
        lang = os.getenv('BOT_LOCALE', 'en_US')
    
    try:
        with open(f'locales/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to English if locale file not found
        with open('locales/en_US.json', 'r', encoding='utf-8') as f:
            return json.load(f)

# Load locale from environment variable
locale = load_locale()

# Connect to SQLite database
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        entry_count INTEGER DEFAULT 0,
        last_call_time TIMESTAMP
    )
''')

conn.commit()

# Dictionary of messages per channel
channel_messages = {}
for i in range(1, 11):  # Limit of 10 channels
    channel_env = f'CHANNEL_{i}'
    channel_id = os.getenv(channel_env)
    if channel_id:
        channel_messages[channel_id] = locale["user_in_channel"].format(member="{member.name}", channel="{channel_name}")
    else:
        break  # Stop the loop if there are no more defined channels

# Variable to control the state of sending messages when someone enters a call
send_message_enabled = True

# Check if logs should be displayed
show_log = os.getenv('SHOW_LOG', 'false').lower() == 'true'

@client.event
async def on_ready():
    rich_presence = os.getenv('RICH_PRESENCE', 'Katchau!')
    activity = os.getenv('ACTIVITY', 'playing').lower()
    activity_type = discord.ActivityType.playing
    if activity == 'listening':
        activity_type = discord.ActivityType.listening
    elif activity == 'watching':
        activity_type = discord.ActivityType.watching
    elif activity == 'streaming':
        activity_type = discord.ActivityType.streaming
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name=rich_presence, type=activity_type))
    print('Bot online!')
    print(f'Connected as {client.user.name}')
    print('------')

@client.event
async def on_voice_state_update(member, before, after):
    global send_message_enabled

    if not send_message_enabled:
        return

    if before.channel == after.channel:
        return  # Ignore updates that don't involve channel changes

    notification_channel_id = os.getenv('NOTIFICATION_CHANNEL')
    if not notification_channel_id:
        return
    
    channel = client.get_channel(int(notification_channel_id))
    if not channel:
        return

    # User joined a voice channel
    if after.channel:
        if len(after.channel.members) == 1:
            # First person in the channel - mark with @everyone
            await channel.send(locale["user_joined_call"].format(member=member.mention))

            # Update entry count and last call time in the database
            cursor.execute('''
                INSERT OR REPLACE INTO users (id, name, entry_count, last_call_time)
                VALUES (?, ?, COALESCE((SELECT entry_count FROM users WHERE id = ?) + 1, 1), ?)
            ''', (member.id, member.name, member.id, datetime.now()))
            conn.commit()

            if show_log:
                print(f"{member.name} entered a channel.")
        else:
            # Other people joining - just show channel info
            await channel.send(locale["user_in_channel"].format(member=member.name, channel=after.channel.name))
    
    # User left a voice channel
    if before.channel and not after.channel:
        await channel.send(locale["user_left_channel"].format(member=member.name, channel=before.channel.name))
    
    # User moved between channels
    if before.channel and after.channel and before.channel != after.channel:
        await channel.send(locale["user_moved_to_channel"].format(
            member=member.name, 
            old_channel=before.channel.name, 
            new_channel=after.channel.name
        ))
        
        if show_log:
            print(f"{member.name} was moved from {before.channel.name} to {after.channel.name}")

@slash.slash(name="leaders", description="Shows how many times each user entered calls.")
async def leaders(ctx):
    cursor.execute('SELECT id, name, entry_count FROM users ORDER BY entry_count DESC LIMIT 10')
    leaderboard = cursor.fetchall()
    leaderboard_text = locale["leaderboard_title"] + "\n"
    for idx, (user_id, name, count) in enumerate(leaderboard, start=1):
        leaderboard_text += locale["leaderboard_entry"].format(position=idx, name=name, count=count) + "\n"
    await ctx.send(content=leaderboard_text)
    if show_log:
        print('Leaderboard command executed.')

@slash.slash(name="toggle", description="Turns on/off the functionality of sending a message when someone enters a call.")
async def toggle_message(ctx):
    global send_message_enabled
    send_message_enabled = not send_message_enabled
    status = locale["toggle_enabled"] if send_message_enabled else locale["toggle_disabled"]
    await ctx.send(content=status)

@slash.slash(name="help", description="Get a list of commands.")
async def help(ctx):
    commands = [
        locale["help_leaders"],
        locale["help_toggle"],
        locale["help_help"]
    ]
    command_list = "\n".join(commands)
    await ctx.send(content=locale["help_title"].format(author=ctx.author.name) + "\n\n" + command_list)

# Load the bot token from environment variables
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    raise ValueError("Bot token not found. Make sure to set the DISCORD_BOT_TOKEN environment variable.")

client.run(TOKEN)
