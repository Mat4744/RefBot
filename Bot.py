# Libraries
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from initialize_database import initialize_database

# Token Retrieval
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents Setup
intents = discord.Intents.default()
intents.message_content = True  # To process messages
intents.guilds = True
intents.members = True

# Bot Setup
bot = commands.Bot(command_prefix='*', intents=intents)

# Bot Database Setup
initialize_database()

# Bot Startup
@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    for guild in bot.guilds:
        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
        if channel:
            await channel.send("Hello Evershade! RefBot is now online.")

# Error
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occurred: {error}")

# Simple bot answering command test
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Run the Bot
bot.run(TOKEN)