import sqlite3

def init_db():
    connection = sqlite3.connect("reminders.db")
    connection.execute("PRAGMA foreign_keys = ON")
    c = connection.cursor()
    
    # Users Table
    c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                language TEXT NOT NULL,
                current_hour TEXT
            )""")
    
    # Reminders Table
    c.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                hour TEXT,
                text TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
                )""")
    
    connection.commit()
    connection.close()

if __name__ == "__main__":
    init_db()