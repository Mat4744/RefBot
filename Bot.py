# Libraries
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Token Retrieval
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages, intents.guilds, intents.members = True, True, True

bot = commands.Bot(command_prefix='*', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    for guild in bot.guilds:
        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
        if channel:
            await channel.send("Hello Evershade! RefBot is now online.")

bot.run(TOKEN)