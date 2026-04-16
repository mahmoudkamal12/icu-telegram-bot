# migrate_data.py
import json
import asyncio
import aiosqlite
import db_utils # Imports DB_PATH and init_db from your db_utils.py

# Define the names of your JSON files
ACTIVE_USERS_FILE = "active_users.json"
PROGRESS_FILE = "progress.json"
POLL_DATA_FILE = "poll_data.json"

async def migrate_active_users(db):
    print(f"Starting migration for {ACTIVE_USERS_FILE}...")
    try:
        with open(ACTIVE_USERS_FILE, "r") as f:
            active_users_list = json.load(f)
    except FileNotFoundError:
        print(f"'{ACTIVE_USERS_FILE}' not found. Skipping active users migration.")
        return
    except json.JSONDecodeError:
        print(f"Error decoding '{ACTIVE_USERS_FILE}'. Skipping active users migration.")
        return

    if not isinstance(active_users_list, list):
        print(f"Content of '{ACTIVE_USERS_FILE}' is not a list. Skipping active users migration.")
        return

    migrated_count = 0
    for user_id in active_users_list:
        try:
            user_id_int = int(user_id) # Ensure user_id is integer
            # Using INSERT OR IGNORE to avoid errors if a user_id is duplicated in the JSON
            # or if the script is run multiple times.
            await db.execute(
                "INSERT OR IGNORE INTO active_users (user_id) VALUES (?)",
                (user_id_int,)
            )
            migrated_count += 1
        except ValueError:
            print(f"Warning: Invalid user_id format '{user_id}' in '{ACTIVE_USERS_FILE}'. Skipping this entry.")
        except Exception as e:
            print(f"Error inserting user_id {user_id} into active_users: {e}")

    await db.commit()
    print(f"Migrated {migrated_count} users from '{ACTIVE_USERS_FILE}' to 'active_users' table.")

async def migrate_progress_data(db):
    print(f"Starting migration for {PROGRESS_FILE}...")
    progress_data_content = {} # To store loaded data for poll_data migration
    try:
        with open(PROGRESS_FILE, "r") as f:
            progress_data_content = json.load(f)
    except FileNotFoundError:
        print(f"'{PROGRESS_FILE}' not found. Skipping progress data migration.")
        return progress_data_content # Return empty dict
    except json.JSONDecodeError:
        print(f"Error decoding '{PROGRESS_FILE}'. Skipping progress data migration.")
        return progress_data_content

    if not isinstance(progress_data_content, dict):
        print(f"Content of '{PROGRESS_FILE}' is not a dictionary. Skipping progress data migration.")
        return {} # Return empty dict as content is not as expected

    migrated_entries = 0
    for user_id_str, attempts in progress_data_content.items():
        try:
            user_id = int(user_id_str)
            if not isinstance(attempts, list):
                print(f"Warning: Data for user {user_id} in '{PROGRESS_FILE}' is not a list. Skipping this user.")
                continue

            for attempt in attempts:
                if not isinstance(attempt, dict):
                    print(f"Warning: Attempt for user {user_id} (value: {attempt}) is not a dictionary. Skipping this attempt.")
                    continue

                poll_id = attempt.get("poll_id")
                question = attempt.get("question")
                # Ensure options is a list, default to empty if missing or not a list
                options_list = attempt.get("options", [])
                if not isinstance(options_list, list):
                    print(f"Warning: Options for user {user_id}, poll_id {poll_id} are not a list (value: {options_list}). Using empty list.")
                    options_list = []
                
                correct_index = attempt.get("correct_index")
                explanation = attempt.get("explanation", "No explanation provided.") # Default explanation

                if not all([poll_id, question, correct_index is not None]):
                    print(f"Warning: Missing critical data in attempt for user {user_id}, poll_id '{poll_id}'. Skipping this attempt.")
                    continue
                
                await db.execute(
                    """
                    INSERT OR IGNORE INTO user_quiz_progress
                    (user_id, poll_id, question, options, correct_index, explanation)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        str(poll_id), # Ensure poll_id is string
                        question,
                        json.dumps(options_list), # Serialize list to JSON string
                        correct_index,
                        explanation,
                    ),
                )
                migrated_entries += 1
        except ValueError:
            print(f"Warning: Invalid user_id format '{user_id_str}' in '{PROGRESS_FILE}'. Skipping this user.")
        except Exception as e:
            print(f"Error processing progress for user '{user_id_str}': {e}")
    await db.commit()
    print(f"Migrated {migrated_entries} entries from '{PROGRESS_FILE}' to 'user_quiz_progress' table.")
    return progress_data_content # Return loaded data for poll_data migration

async def migrate_poll_data(db, progress_data_from_json):
    print(f"Starting migration for {POLL_DATA_FILE}...")
    try:
        with open(POLL_DATA_FILE, "r") as f:
            poll_data_from_json_file = json.load(f)
    except FileNotFoundError:
        print(f"'{POLL_DATA_FILE}' not found. Skipping poll data migration.")
        return
    except json.JSONDecodeError:
        print(f"Error decoding '{POLL_DATA_FILE}'. Skipping poll data migration.")
        return

    if not isinstance(poll_data_from_json_file, dict):
        print(f"Content of '{POLL_DATA_FILE}' is not a dictionary. Skipping poll data migration.")
        return

    migrated_count = 0
    for poll_id_str, data in poll_data_from_json_file.items():
        try:
            options_for_poll = [] # Default
            found_options = False
            
            # Search progress_data_from_json (passed as argument) for options related to this poll_id
            if progress_data_from_json: # Check if progress data was loaded and passed
                for user_key in progress_data_from_json: # Iterate through user IDs (keys)
                    user_attempts = progress_data_from_json[user_key]
                    if isinstance(user_attempts, list):
                        for attempt in user_attempts:
                            if isinstance(attempt, dict) and attempt.get("poll_id") == poll_id_str and "options" in attempt:
                                if isinstance(attempt["options"], list):
                                    options_for_poll = attempt["options"]
                                    found_options = True
                                    break
                                else:
                                    print(f"Warning: Options for poll_id {poll_id_str} found in progress data but are not a list. Using empty list.")
                    if found_options:
                        break
            
            if not found_options:
                print(f"Warning: Options not found in loaded progress data for poll_id '{poll_id_str}'. Poll will be stored with an empty options list.")

            question = data.get("question", "N/A") # Default question
            correct_index = data.get("correct_index")
            explanation = data.get("explanation", "N/A") # Default explanation

            if correct_index is None: # correct_index is critical
                print(f"Warning: Missing 'correct_index' for poll_id '{poll_id_str}' in '{POLL_DATA_FILE}'. Skipping this poll entry.")
                continue

            await db.execute(
                """
                INSERT OR IGNORE INTO current_polls (poll_id, question, options, correct_index, explanation)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(poll_id_str), # Ensure poll_id is string
                    question,
                    json.dumps(options_for_poll), # Serialize list to JSON string
                    correct_index,
                    explanation,
                ),
            )
            migrated_count += 1
        except Exception as e:
            print(f"Error processing poll_data for poll_id '{poll_id_str}': {e}")

    await db.commit()
    print(f"Migrated {migrated_count} entries from '{POLL_DATA_FILE}' to 'current_polls' table.")


async def main_migration_logic():
    print("Starting database migration script...")
    # 1. Initialize database (create tables if they don't exist)
    # This ensures the db file and schema are ready.
    await db_utils.init_db()

    # 2. Open a connection for the actual migration operations
    async with aiosqlite.connect(db_utils.DB_PATH) as db:
        # Migrate active users
        await migrate_active_users(db)

        # Migrate progress data (and get its content for poll options retrieval)
        progress_content_from_json = await migrate_progress_data(db)

        # Migrate poll data, using content from progress.json to find options
        await migrate_poll_data(db, progress_content_from_json)

    print("-" * 30)
    print("Migration process completed.")
    print(f"Your data should now be in the SQLite database: '{db_utils.DB_PATH}'.")
    print("IMPORTANT: Please verify the contents using 'sqlite3 bot_data.db' and SQL commands (e.g., SELECT COUNT(*) FROM ...).")
    print("Also, backup your original JSON files and the new 'bot_data.db' file before proceeding with bot code changes.")
    print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main_migration_logic())