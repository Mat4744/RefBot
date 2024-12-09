import sqlite3

def initialize_database():
    conn = sqlite3.connect('refbot.db')  # Creates or connects to the database file
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
        downtime_days INTEGER DEFAULT 0,
        gold INTEGER DEFAULT 0,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Call this function when the bot starts
initialize_database()