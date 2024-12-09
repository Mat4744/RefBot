import os
import sqlite3
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Token Retrieval
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# SQLite Database Setup
DB_PATH = 'refbot.db'

# Intents Setup
intents = discord.Intents.default()
intents.message_content = True  # To process messages
intents.guilds = True
intents.members = True

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Characters table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Characters (
        character_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        resurrections INTEGER DEFAULT 0,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    ''')

    conn.commit()
    conn.close()

# Initialize database
initialize_database()

# Bot Setup
bot = commands.Bot(command_prefix='*', intents=intents)

# Bot Startup
@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    for guild in bot.guilds:
        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
        if channel:
            await channel.send("Hello Evershade! RefBot is now online.")

# Simple bot answering command test
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def setup(ctx):
    user_id = str(ctx.author.id)
    username = ctx.author.name

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if the user exists in the database
    cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if not user:
        # If the user doesn't exist, add them to the database
        cursor.execute('INSERT INTO Users (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        await ctx.send(f"Welcome to the server, {username}! Let's set up your roster.")

        # Request character details
        await ctx.send("Please provide your characters in the following format:\n`Name, Level, Resurrections, Description`\nSeparate multiple characters with a semicolon `;`.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            message = await bot.wait_for('message', check=check, timeout=60.0)
            character_entries = message.content.split(';')

            for entry in character_entries:
                parts = [p.strip() for p in entry.split(',')]
                if len(parts) == 4:
                    name, level, resurrections, description = parts
                    cursor.execute(
                        'INSERT INTO Characters (user_id, name, level, resurrections, description) VALUES (?, ?, ?, ?, ?)',
                        (user_id, name, int(level), int(resurrections), description)
                    )
                else:
                    await ctx.send(f"Invalid format for character: `{entry}`. Please try again.")
                    conn.rollback()
                    return

            conn.commit()
            await ctx.send("Your roster has been successfully set up!")
        except Exception as e:
            await ctx.send("You took too long to respond or an error occurred. Please try again.")
    else:
        # If the user exists, redirect them to EditRoster
        await ctx.send(f"You already have a roster set up, {username}. Did you mean to use the `EditRoster` command?")

    conn.close()

# Run the Bot
bot.run(TOKEN)