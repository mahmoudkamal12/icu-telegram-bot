import asyncio
import aiosqlite

async def debug_db():
    DB_PATH = "bot_data.db"
    try:
        async with aiosqlite.connect(DB_PATH, timeout=5) as db:
            async with db.execute("SELECT user_id FROM active_users LIMIT 5") as cursor:
                active = await cursor.fetchall()
                print(f"Active users (first 5): {active}")
            
            async with db.execute("SELECT DISTINCT user_id FROM user_quiz_progress LIMIT 5") as cursor:
                progress = await cursor.fetchall()
                print(f"Progress users (first 5): {progress}")
                
            async with db.execute("SELECT user_id FROM active_users UNION SELECT user_id FROM user_quiz_progress LIMIT 5") as cursor:
                combined = await cursor.fetchall()
                print(f"Combined users (first 5): {combined}")
    except Exception as e:
        print(f"Error accessing DB: {e}")

if __name__ == "__main__":
    asyncio.run(debug_db())
