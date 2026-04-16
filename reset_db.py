import sqlite3
import os

DB_PATH = "bot_data.db"

def reset_database():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} does not exist. Nothing to clear.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear all tables
        tables = ["user_quiz_progress", "active_users", "current_polls"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Cleared table: {table}")
            
        conn.commit()
        conn.close()
        print("Database reset successful! All questions and progress have been cleared.")
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
