import asyncio
import logging
from telegram import Bot
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_bot_info():
    bot = Bot(token=BOT_TOKEN)
    
    new_name = "MK_ICU_MCQ"
    new_description = "ICU Quiz Bot for EDIC preparation and clinical learning."
    new_short_description = "Master ICU concepts with daily MCQs."

    try:
        # Set the bot's display name
        logger.info(f"Setting bot name to: {new_name}")
        await bot.set_my_name(name=new_name)
        
        # Set the bot's description (shown in 'About' and when starting)
        logger.info(f"Setting bot description...")
        await bot.set_my_description(description=new_description)
        
        # Set the bot's short description (shown on the bot's profile page)
        logger.info(f"Setting bot short description...")
        await bot.set_my_short_description(short_description=new_short_description)
        
        logger.info("Bot info updated successfully! It may take a few minutes to reflect in all Telegram clients.")
    except Exception as e:
        logger.error(f"Failed to update bot info: {e}")

if __name__ == "__main__":
    asyncio.run(update_bot_info())
