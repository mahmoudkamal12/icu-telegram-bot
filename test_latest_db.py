import asyncio
import db_utils
from tiktok_video_gen import background_video_task

async def generate_from_latest_db():
    print("Fetching the latest question from the database...")
    questions = await db_utils.get_all_distinct_questions_db()
    
    if not questions:
        print("Error: No questions found in the database!")
        return
        
    latest = questions[0]
    question = latest['question']
    options = latest['options']
    correct_index = latest['correct_index']
    explanation = latest['explanation']
    
    print("Found latest question:")
    print(f"Q: {question[:100].encode('ascii', 'ignore').decode()}...")
    print(f"Generating TikTok video in the background...")
    
    await background_video_task(question, options, correct_index, explanation)
    print("Video generation completed!")

if __name__ == "__main__":
    asyncio.run(generate_from_latest_db())
