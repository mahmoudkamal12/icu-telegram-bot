# db_utils.py
import aiosqlite
import logging
import json # For serializing/deserializing list options
from datetime import datetime, timedelta
from typing import Optional # Added for type hinting Optional[dict]

logger = logging.getLogger(__name__)
DB_PATH = "bot_data.db" # This file will be created in the same directory
DB_TIMEOUT = 20.0  # Increased busy timeout to 20 seconds

async def init_db():
    # WAL mode should be set on a connection.
    # It only needs to be successfully executed once for the database file.
    # Subsequent executions of this PRAGMA on a DB already in WAL mode are harmless.
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        try:
            await db.execute("PRAGMA journal_mode=WAL;")
            async with db.execute("PRAGMA journal_mode;") as cursor: # Verify
                current_mode = await cursor.fetchone()
                logger.info(f"Database journal_mode set/verified to: {current_mode[0] if current_mode else 'UNKNOWN'}")
        except Exception as e:
            logger.error(f"Could not set/verify journal_mode to WAL: {e}")

        # User progress table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_quiz_progress (
                user_id INTEGER NOT NULL,
                poll_id TEXT NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL, -- Store as JSON string
                correct_index INTEGER NOT NULL,
                user_answer_index INTEGER, -- Added for performance tracking
                is_correct BOOLEAN,        -- Added for performance tracking
                explanation TEXT,
                aspect TEXT, -- Added for round-robin logic
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, poll_id)
            )
        """)
        
        # Migration: Add new columns if they don't exist
        try:
            await db.execute("ALTER TABLE user_quiz_progress ADD COLUMN aspect TEXT")
            logger.info("Added aspect column to user_quiz_progress.")
        except Exception: pass # Already exists
        try:
            await db.execute("ALTER TABLE user_quiz_progress ADD COLUMN user_answer_index INTEGER")
            logger.info("Added user_answer_index column to user_quiz_progress.")
        except Exception: pass
        try:
            await db.execute("ALTER TABLE user_quiz_progress ADD COLUMN is_correct BOOLEAN")
            logger.info("Added is_correct column to user_quiz_progress.")
        except Exception: pass

        await db.execute("CREATE INDEX IF NOT EXISTS idx_user_question ON user_quiz_progress (user_id, question)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_question ON user_quiz_progress (question)")

        # Active users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_users (
                user_id INTEGER PRIMARY KEY,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Current polls table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS current_polls (
                poll_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                options TEXT NOT NULL, -- Store original options sent with the poll as JSON string
                correct_index INTEGER NOT NULL,
                explanation TEXT,
                aspect TEXT, -- Added for round-robin logic
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bot events table for analytics
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bot_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                event_type TEXT NOT NULL -- 'poll_sent', 'command_next', etc.
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_poll_created_at ON current_polls (created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_event_timestamp ON bot_events (timestamp)")

        await db.commit()
        logger.info(f"Database '{DB_PATH}' schema initialized/verified.")

# --- User Quiz Progress Functions ---
async def save_quiz_for_user_db(user_id: int, poll_id: str, question: str, options: list, correct_index: int, 
                               explanation: str, aspect: str = None, user_answer_index: int = None):
    is_correct = (user_answer_index == correct_index) if user_answer_index is not None else None
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO user_quiz_progress
            (user_id, poll_id, question, options, correct_index, user_answer_index, is_correct, explanation, aspect)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, poll_id, question, json.dumps(options), correct_index, user_answer_index, is_correct, explanation, aspect)
        )
        await db.commit()
        logger.debug(f"Saved quiz progress for user {user_id}, poll {poll_id} with aspect {aspect}. Correct: {is_correct}")

async def log_event_db(event_type: str, user_id: int = None):
    """Logs a bot event (e.g., 'poll_sent', 'command_next') for analytics."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        await db.execute(
            "INSERT INTO bot_events (event_type, user_id) VALUES (?, ?)",
            (event_type, user_id)
        )
        await db.commit()

async def get_analytics_summary_db():
    """Returns a dictionary of key metrics for the dashboard."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        stats = {}
        
        # Total Users
        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM active_users") as c:
            row = await c.fetchone()
            stats['total_users'] = row[0] if row else 0
            
        # Total Questions Sent (Events)
        async with db.execute("SELECT COUNT(*) FROM bot_events WHERE event_type = 'poll_sent'") as c:
            row = await c.fetchone()
            stats['polls_sent'] = row[0] if row else 0

        # Total Answered (Historical)
        async with db.execute("SELECT COUNT(*) FROM user_quiz_progress") as c:
            row = await c.fetchone()
            stats['polls_answered'] = row[0] if row else 0
            
        # Accuracy
        async with db.execute("SELECT COUNT(*) FROM user_quiz_progress WHERE is_correct = 1") as c:
            row = await c.fetchone()
            stats['correct_answers'] = row[0] if row else 0
            
        # /next usage
        async with db.execute("SELECT COUNT(*) FROM bot_events WHERE event_type = 'command_next'") as c:
            row = await c.fetchone()
            stats['next_commands'] = row[0] if row else 0
            
        return stats

async def get_seen_questions_for_user_db(user_id: int) -> set:
    """Returns a set of question strings that the user has seen (answered)."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute("SELECT DISTINCT question FROM user_quiz_progress WHERE user_id = ?", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return {row[0] for row in rows}

async def get_all_distinct_questions_db() -> list:
    """
    Gets all distinct questions from the current_polls table.
    Each item is a dict: {"question": str, "options": list, "correct_index": int, "explanation": str, "aspect": str}
    """
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        questions_list = []
        async with db.execute("SELECT question, options, correct_index, explanation, aspect FROM current_polls ORDER BY created_at DESC") as cursor:
            async for row in cursor:
                try:
                    options_list = json.loads(row[1])
                    if not isinstance(options_list, list): options_list = []
                except json.JSONDecodeError:
                    options_list = []

                questions_list.append({
                    "question": row[0],
                    "options": options_list,
                    "correct_index": row[2],
                    "explanation": row[3],
                    "aspect": row[4]
                })
    return questions_list


async def get_recent_aspects_for_user_db(user_id: int, limit: int = 10) -> list:
    """Returns a list of aspect names recently seen by the user."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute(
            "SELECT aspect FROM user_quiz_progress WHERE user_id = ? AND aspect IS NOT NULL ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def get_saved_question_by_poll_id_db(user_id: int, poll_id: str) -> Optional[dict]:
    """ Retrieves a specific quiz attempt by a user for a given poll_id. """
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute(
            "SELECT question, options, correct_index, explanation, aspect FROM user_quiz_progress WHERE user_id = ? AND poll_id = ?",
            (user_id, poll_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                try:
                    options_list = json.loads(row[1])
                    if not isinstance(options_list, list): options_list = []
                except json.JSONDecodeError:
                    options_list = []
                return {
                    "question": row[0],
                    "options": options_list,
                    "correct_index": row[2],
                    "explanation": row[3],
                    "aspect": row[4]
                }
            return None

# --- Active Users Functions ---
async def add_active_user_db(user_id: int):
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        await db.execute("INSERT OR IGNORE INTO active_users (user_id) VALUES (?)", (user_id,))
        await db.commit()
        logger.info(f"User {user_id} marked as active.")

async def remove_active_user_db(user_id: int):
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        await db.execute("DELETE FROM active_users WHERE user_id = ?", (user_id,))
        await db.commit()
        logger.info(f"User {user_id} marked as inactive.")

async def is_user_active_db(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute("SELECT 1 FROM active_users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone() is not None

async def get_all_active_users_db() -> set:
    """Returns a set of user_ids for all active users."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute("SELECT user_id FROM active_users") as cursor:
            rows = await cursor.fetchall()
            return {row[0] for row in rows}

# --- Current Polls Functions ---
POLL_DATA_EXPIRY_DAYS = 7

async def save_poll_data_db(poll_id: str, question: str, options: list, correct_index: int, explanation: str, aspect: str = None):
    """Saves details of a sent poll, including its options."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO current_polls (poll_id, question, options, correct_index, explanation, aspect)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (poll_id, question, json.dumps(options), correct_index, explanation, aspect)
        )
        await db.commit()
        logger.info(f"Successfully saved poll {poll_id} with aspect: {aspect}")

async def get_poll_data_db(poll_id: str) -> Optional[dict]:
    """Retrieves data for a specific poll, including its options."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute(
            "SELECT question, options, correct_index, explanation, aspect FROM current_polls WHERE poll_id = ?", (poll_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                try:
                    options_list = json.loads(row[1])
                    if not isinstance(options_list, list):
                        options_list = []
                        logger.warning(f"Corrupted options for poll {poll_id} in DB (not a list), loaded as empty.")
                except json.JSONDecodeError:
                    options_list = []
                    logger.warning(f"JSONDecodeError for options on poll {poll_id}, loaded as empty.")

                return {
                    "question": row[0],
                    "options": options_list,
                    "correct_index": row[2],
                    "explanation": row[3],
                    "aspect": row[4]
                }
            return None

async def prune_database_to_limit_db(limit: int = 500):
    """Keeps only the most recent 'limit' questions across current_polls and cleans up references."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        # 1. Identity poll_ids to KEEP (the 100 most recent)
        async with db.execute("SELECT poll_id FROM current_polls ORDER BY created_at DESC LIMIT ?", (limit,)) as cursor:
            keep_ids = [row[0] for row in (await cursor.fetchall())]
        
        if not keep_ids: return

        # 2. Delete from current_polls where not in keep list
        placeholders = ', '.join(['?' for _ in keep_ids])
        await db.execute(f"DELETE FROM current_polls WHERE poll_id NOT IN ({placeholders})", keep_ids)
        
        # NOTE: WE NO LONGER DELETE FROM user_quiz_progress HERE. 
        # This ensures the bot never 'forgets' that a user has seen a question, 
        # even if that question is removed from the active rotation.
        
        await db.commit()
        logger.info(f"Database pruned to maintain {len(keep_ids)} recent polls. User progress preserved.")

async def cleanup_old_poll_data_db():
    """Old cleanup function, now superseded by prune_database_to_limit_db but kept for compatibility."""
    await prune_database_to_limit_db(500)


# --- Utility/Stats Functions (as provided by user) ---
async def get_total_users_db() -> int:
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM user_quiz_progress") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_total_saved_questions_db() -> int:
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute("SELECT COUNT(*) FROM user_quiz_progress") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_total_active_users_db() -> int:
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        async with db.execute("SELECT COUNT(*) FROM active_users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_all_user_ids_db() -> list:
    """Returns a list of all distinct user_ids from user_quiz_progress and active_users."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
        query = "SELECT user_id FROM active_users UNION SELECT user_id FROM user_quiz_progress"
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


if __name__ == '__main__':
    import asyncio
    async def test_db_init_and_wal():
        await init_db() # This will also attempt to set WAL and log it.
        print(f"Database schema in '{DB_PATH}' should be ready.")
        # Explicitly check WAL mode after init_db has run
        async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT) as db:
            async with db.execute("PRAGMA journal_mode;") as cursor:
                mode = await cursor.fetchone()
                print(f"Verification: Current journal_mode is: {mode[0] if mode else 'Could not verify'}")

    asyncio.run(test_db_init_and_wal())
