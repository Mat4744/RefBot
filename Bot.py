import os
import sqlite3
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ui import View, Button, Select

# Token and Database Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_PATH = 'refbot.db'
STAFF_ROLES = ["Refs", "Arena Overseer", "Maruts", "Dark Lords", "Lore Keepers"]

# Intents
intents = discord.Intents.default()
intents.message_content = intents.guilds = intents.members = True

# Database Initialization
def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Create Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                            user_id TEXT PRIMARY KEY, 
                            username TEXT NOT NULL, 
                            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create Characters table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Characters (
                            character_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT, 
                            name TEXT NOT NULL, 
                            level INTEGER DEFAULT 1, 
                            resurrections INTEGER DEFAULT 0,
                            downtime_days FLOAT DEFAULT 0,  
                            description TEXT, 
                            active_character BOOLEAN DEFAULT 0, 
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
    if not cursor.fetchone():
        cursor.execute('INSERT INTO Users (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        await ctx.send(f"Welcome, {username}! Let's set up your roster.")
    elif cursor.execute('SELECT * FROM Characters WHERE user_id = ?', (user_id,)).fetchall():
        await ctx.send(f"Roster already exists, {username}. Try `EditRoster`.")
        return
    else:
        await ctx.send(f"You exist in the system but have no characters yet. Let's fix that!")

    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    character_list, invalid_attempts = [], 0

    while True:
        await ctx.send("Add characters as `Name, Level, Resurrections` or type `done` to finish.")
        try:
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
                    invalid_attempts = 0  # Reset invalid attempts on success
                    await ctx.send("Current roster:\n" +
                                   "\n".join(f"{i+1}. {c['name']} (Level: {c['level']}, Resurrections: {c['resurrections']})"
                                             for i, c in enumerate(character_list)))
                except ValueError:
                    invalid_attempts += 1
            else:
                invalid_attempts += 1

            if invalid_attempts > 5:
                await ctx.send("You know what, screw you. I'm deleting your characters.")
                conn.rollback()
                return
            elif invalid_attempts > 0:
                messages = [
                    "Invalid format! Please use: Name, Level, Resurrections.",
                    "Invalid format, again! Please use my format?",
                    "Please use the provided format!",
                    "The format, sir/ma'am.",
                    "This bitch... The format, follow the format!"
                ]
                await ctx.send(messages[min(invalid_attempts - 1, len(messages) - 1)])

        except Exception as e:
            await ctx.send(f"Error occurred: {e}. Try again!")
            conn.rollback()
            return
    conn.close()

@bot.command()
async def edit(ctx, character_name: str = None, field: str = None, value: str = None):
    user_id = str(ctx.author.id)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # If no arguments are provided, show a list of characters and editing options
    if not character_name:
        cursor.execute('SELECT name, level, resurrections, downtime_days FROM Characters WHERE user_id = ?', (user_id,))
        characters = cursor.fetchall()

        if not characters:
            await ctx.send("You have no characters to edit. Use `*setup` to create your roster.")
        else:
            character_list = "\n".join(
                f"{i+1}. {c[0]} (Level: {c[1]}, Resurrections: {c[2]}, Downtime Days: {c[3]})"
                for i, c in enumerate(characters)
            )
            await ctx.send(f"Here are your characters:\n{character_list}\n"
                           "To edit, use: `*edit <character_name> <field> <value>`\n"
                           "Valid fields: `level`, `resurrections`, `downtime`, `delete`.")
        conn.close()
        return

    # Check if the character exists for the user
    cursor.execute(
        'SELECT * FROM Characters WHERE user_id = ? AND name = ?', (user_id, character_name)
    )
    character = cursor.fetchone()

    if not character:
        await ctx.send(f"Character `{character_name}` does not exist in your roster.")
        conn.close()
        return

    # Handle the `delete` command
    if field and field.lower() == "delete":
        cursor.execute(
            'DELETE FROM Characters WHERE user_id = ? AND name = ?', (user_id, character_name)
        )
        conn.commit()
        await ctx.send(f"Character `{character_name}` has been deleted from your roster.")
        conn.close()
        return

    # Map valid fields to their database columns
    valid_fields = {
        "level": "level",
        "resurrections": "resurrections",
        "downtime": "downtime_days",
    }

    if not field or field.lower() not in valid_fields:
        await ctx.send(
            f"Invalid or missing field `{field}`. You can edit: `level`, `resurrections`, `downtime`, or `delete`."
        )
        conn.close()
        return

    # Validate value for numerical fields
    if field.lower() in ["level", "resurrections", "downtime"]:
        try:
            value = float(value) if field.lower() == "downtime" else int(value)
        except ValueError:
            await ctx.send(f"Invalid value `{value}` for `{field}`. Please provide a valid number.")
            conn.close()
            return

    # Update the field in the database
    db_field = valid_fields[field.lower()]
    cursor.execute(
        f'UPDATE Characters SET {db_field} = ? WHERE user_id = ? AND name = ?',
        (value, user_id, character_name)
    )
    conn.commit()
    await ctx.send(f"Character `{character_name}` updated: `{field}` is now `{value}`.")

    conn.close()

bot.run(TOKEN)