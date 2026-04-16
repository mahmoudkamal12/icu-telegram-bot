import asyncio
import aiosqlite

async def clear_questions():
    DB_PATH = "bot_data.db"
    try:
        async with aiosqlite.connect(DB_PATH, timeout=20) as db:
            print("Clearing user_quiz_progress...")
            await db.execute("DELETE FROM user_quiz_progress")
            
            print("Clearing current_polls...")
            await db.execute("DELETE FROM current_polls")
            
            await db.commit()
            print("Successfully deleted all questions and history from the database! ✅")
    except Exception as e:
        print(f"Error clearing database: {e}")

if __name__ == "__main__":
    asyncio.run(clear_questions())
