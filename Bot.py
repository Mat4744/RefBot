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
        await ctx.send(f"Hello there, {username}! Welcome to 5e Fight Club. Let's set up your roster, shall we?")

        character_list = []
        invalid_attempts = 0

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        while True:
            try:
                # Ask for character details
                await ctx.send("Provide your character in the following format:\n`Name, Level, Resurrections, Description`\nType `done` when you're finished adding characters.")
                message = await bot.wait_for('message', check=check, timeout=60.0)

                if message.content.lower() == 'done':
                    if not character_list:
                        await ctx.send("You didn't add any characters. Start over if you wish to try again!")
                        conn.rollback()
                        return
                    else:
                        # Confirm and save characters to the database
                        for character in character_list:
                            cursor.execute(
                                'INSERT INTO Characters (user_id, name, level, resurrections, description) VALUES (?, ?, ?, ?, ?)',
                                (user_id, character['name'], character['level'], character['resurrections'], character['description'])
                            )
                        conn.commit()
                        await ctx.send("Your roster has been successfully set up!")
                        break

                # Parse character input
                parts = [p.strip() for p in message.content.split(',')]
                if len(parts) == 4:
                    name, level, resurrections, description = parts
                    character = {
                        'name': name,
                        'level': int(level),
                        'resurrections': int(resurrections),
                        'description': description
                    }
                    character_list.append(character)

                    # Reset invalid attempts counter
                    invalid_attempts = 0

                    # Display the growing character list
                    roster_preview = "\n".join(
                        [f"{i+1}. {c['name']} (Level: {c['level']}, Resurrections: {c['resurrections']}, Description: {c['description']})"
                         for i, c in enumerate(character_list)]
                    )
                    await ctx.send(f"Current Roster:\n{roster_preview}\nAdd another character or type `done` to finish.")
                else:
                    # Increment invalid attempts
                    invalid_attempts += 1

                    # Custom responses for repeated mistakes
                    if invalid_attempts == 1:
                        await ctx.send("Invalid format! Please use: `Name, Level, Resurrections, Description`.")
                    elif invalid_attempts == 2:
                        await ctx.send("Invalid format, again! Please use my format?")
                    elif invalid_attempts == 3:
                        await ctx.send("Please use the provided format!")
                    elif invalid_attempts == 4:
                        await ctx.send("The format. Please.")
                    elif invalid_attempts == 5:
                        await ctx.send("I-... This is just on purpose isn't it?")
                    else:
                        await ctx.send("You know what, screw this. We start over.")
                        conn.rollback()
                        return

            except Exception as e:
                await ctx.send("Ah! I got distracted, or maybe an error occurred. Either way, please try again!")
                conn.rollback()
                return
    else:
        # If the user exists, redirect them to EditRoster
        await ctx.send(f"You already have a roster set up, {username}. Did you mean to use the `EditRoster` command?")

    conn.close()

# Run the Bot
bot.run(TOKEN)