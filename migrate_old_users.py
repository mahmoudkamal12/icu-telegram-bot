import sqlite3
import os

OLD_DB = r"d:\icu telegram bot\coding\bot_data.db"
NEW_DB = r"d:\icu telegram bot\last version\coding\bot_data.db"

def restore_users():
    if not os.path.exists(OLD_DB):
        print(f"Error: Old DB not found at {OLD_DB}")
        return
    if not os.path.exists(NEW_DB):
        print(f"Error: New DB not found at {NEW_DB}")
        return

    try:
        old_conn = sqlite3.connect(OLD_DB)
        new_conn = sqlite3.connect(NEW_DB)

        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()

        # 1. Restore active_users
        old_cursor.execute("SELECT user_id, started_at FROM active_users")
        users = old_cursor.fetchall()
        
        added_users = 0
        for user in users:
            try:
                new_cursor.execute("INSERT OR IGNORE INTO active_users (user_id, started_at) VALUES (?, ?)", user)
                added_users += 1
            except Exception as e:
                if added_users == 0:
                    print(f"Failed to insert user {user[0]}: {e}")
        
        print(f"Successfully restored {added_users} active users.")

        # 2. Try to restore user_quiz_progress
        added_progress = 0
        try:
            old_cursor.execute("SELECT * FROM user_quiz_progress")
            # get columns
            old_cursor.execute("PRAGMA table_info(user_quiz_progress)")
            old_cols = [col[1] for col in old_cursor.fetchall()]
            
            old_cursor.execute("SELECT * FROM user_quiz_progress")
            progress_rows = old_cursor.fetchall()
            
            placeholders = ",".join(["?"] * len(old_cols))
            col_names = ",".join(old_cols)

            for row in progress_rows:
                try:
                    new_cursor.execute(f"INSERT OR REPLACE INTO user_quiz_progress ({col_names}) VALUES ({placeholders})", row)
                    added_progress += 1
                except Exception as e:
                     pass
        except Exception as e:
            print(f"Progress restore issue: {e}")

        new_conn.commit()
        print(f"Attempted to restore {added_progress} progress records.")

    except Exception as e:
        print(f"Error during restoration: {e}")
    finally:
        old_conn.close()
        new_conn.close()

if __name__ == "__main__":
    restore_users()
