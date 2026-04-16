# run_db_stats.py
import asyncio
from db_utils import get_total_users_db, get_total_saved_questions_db, get_total_active_users_db

async def main():
    total_users = await get_total_users_db()
    total_questions = await get_total_saved_questions_db()
    total_active_user=await get_total_active_users_db()

    print(f"📊 Total unique users: {total_users}")
    print(f"📚 Total saved questions: {total_questions}")
    print(f"👥 Total active users: {total_active_user}")

if __name__ == "__main__":
    asyncio.run(main())
#     print(f"Content of '{PROGRESS_FILE}' is not a dictionary. Skipping progress data migration.")