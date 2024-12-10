import os
import sqlite3
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Token and Database Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_PATH = 'refbot.db'

# Intents
intents = discord.Intents.default()
intents.message_content = intents.guilds = intents.members = True

# Database Initialization
def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                            user_id TEXT PRIMARY KEY, 
                            username TEXT NOT NULL, 
                            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Characters (
                            character_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT, 
                            name TEXT NOT NULL, 
                            level INTEGER DEFAULT 1, 
                            resurrections INTEGER DEFAULT 0, 
                            description TEXT, 
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
                            FOREIGN KEY (user_id) REFERENCES Users(user_id))''')
        conn.commit()

initialize_database()

# Bot Setup
bot = commands.Bot(command_prefix='*', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    for guild in bot.guilds:
        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
        if channel: await channel.send("Hello Evershade! RefBot is now online.")

@bot.command()
async def setup(ctx):
    user_id, username = str(ctx.author.id), ctx.author.name
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
    user_exists = cursor.fetchone()
    if not user_exists:
        cursor.execute('INSERT INTO Users (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        await ctx.send(f"Welcome, {username}! Let's set up your roster.")
    else:
        cursor.execute('SELECT * FROM Characters WHERE user_id = ?', (user_id,))
        if cursor.fetchall():
            await ctx.send(f"Roster already exists, {username}. Try `EditRoster`.")
            return
        await ctx.send(f"You exist in the system but have no characters yet. Let's fix that!")

    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    character_list, invalid_attempts = [], 0

    while True:
        try:
            await ctx.send("Add characters as `Name, Level, Resurrections` or type `done` to finish.")
            msg = await bot.wait_for('message', check=check, timeout=60.0)
            if msg.content.lower() == 'done':
                if not character_list:
                    await ctx.send("No characters added. Try again later!")
                    conn.rollback()
                    return
                try:
                    cursor.executemany(
                        '''INSERT INTO Characters (user_id, name, level, resurrections) VALUES (?, ?, ?, ?)''',
                        [(user_id, c['name'], c['level'], c['resurrections']) for c in character_list])
                    conn.commit()
                    await ctx.send("Roster saved! Here's the final list:\n" + 
                                   "\n".join(f"{i+1}. {c['name']} (Level: {c['level']}, Resurrections: {c['resurrections']})"
                                             for i, c in enumerate(character_list)))
                except Exception as e:
                    await ctx.send(f"Error saving roster: {e}")
                    conn.rollback()
                break
            parts = [p.strip() for p in msg.content.split(',')]
            if len(parts) == 3:
                try:
                    name, level, resurrections = parts[0], int(parts[1]), int(parts[2])
                    character_list.append({'name': name, 'level': level, 'resurrections': resurrections})
                    invalid_attempts = 0
                    await ctx.send("Current roster:\n" + 
                                   "\n".join(f"{i+1}. {c['name']} (Level: {c['level']}, Resurrections: {c['resurrections']})"
                                             for i, c in enumerate(character_list)))
                except ValueError:
                    invalid_attempts += 1
            else:
                invalid_attempts += 1

            messages = [
                "Invalid format! Please use: `Name, Level, Resurrections`.",
                "Invalid format, again! Please use my format?",
                "Please use the provided format!",
                "The format, sir/ma'am.",
                "This bitch... The format, follow the format!",
                "You know what, screw you. I'm deleting your characters."
            ]
            if invalid_attempts > 5:
                await ctx.send(messages[5])
                conn.rollback()
                return
            await ctx.send(messages[min(invalid_attempts - 1, 4)])

        except Exception as e:
            await ctx.send(f"Error occurred: {e}. Try again!")
            conn.rollback()
            return
    conn.close()

bot.run(TOKEN)
