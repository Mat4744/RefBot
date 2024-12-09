from dotenv import load_dotenv
import os

load_dotenv()  # Load the .env file

# Print environment variables
print("DISCORD_TOKEN loaded:", os.getenv('DISCORD_TOKEN'))
