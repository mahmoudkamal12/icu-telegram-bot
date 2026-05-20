# telegram_bot.py
import logging
import os
import re
import json # For db_utils to handle options serialization, not for direct file IO here
import random
import requests
import asyncio
import html # For escaping HTML characters
import traceback # Added for detailed error logging
from datetime import timedelta
import time # Added for monotonic time in caching
from telegram.constants import ParseMode # For Markdown parsing

# --- Your existing imports ---
# Ensure these files and their contents are correctly defined in your project
from config import API_KEY, API_URL, BOT_TOKEN, EDIC_SYSTEM_PROMPT, EDIC_USER_PROMPT, help_text, MODEL_NAME
from icu_chapters import get_random_aspect
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, error as telegram_error
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    PollAnswerHandler,
    CallbackQueryHandler,
)
from telegram.helpers import escape_markdown

# --- Import your database utility functions ---
import db_utils # Your db_utils.py file

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# For more detailed asyncio debugging, you can set:
# logging.getLogger('asyncio').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Constants ---
MAX_SEND_RETRIES = 6
RETRY_INTERVAL_MINUTES = 20
REQUEST_TIMEOUT_SECONDS = 1200  

# --- Global Cache and Rate Limiting ---
ALL_QUESTIONS_CACHE = []
CACHE_MAX_AGE_SECONDS = 3600 # Cache for 1 hour (3600 seconds)
last_questions_cache_update = 0.0 # Using time.monotonic()
model_semaphore = asyncio.Semaphore(1) # Only one generation at a time for local LLM


# --- Local LLM API Call (OpenAI-compatible) ---
def call_model_sync(system_prompt: str, user_prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 4096,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "quiz_question",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "correct_index": {"type": "integer"},
                        "explanation": {"type": "string"}
                    },
                    "required": ["question", "options", "correct_index", "explanation"]
                }
            }
        }
    }

    logger.info(f"Calling Local Model API: {API_URL} with model {MODEL_NAME}")

    try:
        resp = requests.post(API_URL, headers=headers, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error(f"Local API call timed out after {REQUEST_TIMEOUT_SECONDS} seconds.")
        raise TimeoutError(f"Local API call timed out.")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Local API request failed: {req_err}")
        raise

    response_json = resp.json()
    try:
        return response_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing model response: {e} - Response: {response_json}")
        raise ValueError("Failed to get valid content from model response.")

# # --- Clean Response: Extract JSON ---
def clean_response(raw_text: str) -> str:
    """
    Extracts the JSON block from the raw LLM output robustly.
    """
    # 1. Try to find JSON wrapped in ```json ... ``` markdown block
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if json_match:
        try:
            json.loads(json_match.group(1))
            return json_match.group(1).strip()
        except json.JSONDecodeError:
            pass # Fall back to search
            
    # 2. Strip out text before </think> if the model hallucinated it
    # and also handle "Thinking Synchronous:" or "Thinking Process:" headers
    think_end = re.search(r"</(?:think|thought)>|Thinking\s+(?:Synchronous|Process):", raw_text, re.IGNORECASE)
    if think_end:
        raw_text = raw_text[think_end.end():]
        
    # 3. Robust substring extraction: Try parsing from every '{' to the last '}'
    last_brace = raw_text.rfind('}')
    if last_brace == -1:
        return raw_text.strip()
        
    start_idx = raw_text.find('{')
    while start_idx != -1 and start_idx < last_brace:
        substring = raw_text[start_idx:last_brace+1]
        try:
            json.loads(substring)
            return substring # Successfully parsed!
        except json.JSONDecodeError:
            # Move to the next '{'
            start_idx = raw_text.find('{', start_idx + 1)
            
    return raw_text.strip()

# --- Question Parsing ---
def parse_question(raw_text: str):
    try:
        with open("debug_llm.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)
        logger.info(f"Full model output saved to debug_llm.txt.")
    except Exception as e_log:
        logger.error(f"Error saving debug_llm.txt: {e_log}")
    
    logger.info(f"Parsing model output snippet:\n{raw_text[:500]}...")
    
    # Pre-clean: Extract the JSON string robustly
    text = clean_response(raw_text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}\nExtracted text: {text}")
        raise ValueError(f"Failed to parse the quiz format as valid JSON. Extracted: {text[:100]}...")

    question = data.get("question")
    options_raw = data.get("options", [])
    correct_index = data.get("correct_index")
    explanation = data.get("explanation", "No explanation provided.")

    if not question or not options_raw or correct_index is None:
        logger.error(f"Missing required fields in JSON output: {data}")
        raise ValueError("Missing required fields (question, options, or correct_index) in model output.")
        
    if not isinstance(options_raw, list) or len(options_raw) != 4:
        logger.error(f"Options field is invalid: {options_raw}")
        raise ValueError("JSON output does not contain exactly 4 options.")

    options = [str(opt).strip()[:100] for opt in options_raw]
    
    try:
        correct_index = int(correct_index)
        if correct_index < 0 or correct_index > 3:
            raise ValueError()
    except ValueError:
        logger.error(f"Invalid correct_index: {correct_index}")
        raise ValueError("correct_index must be an integer between 0 and 3.")

    return question, options, correct_index, explanation
        
# --- Helper for Forbidden User ---
async def _handle_forbidden_user(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    logger.warning(f"User {user_id} has blocked the bot or bot is not authorized. Deactivating and removing their jobs.")
    job_name = f"quiz_{user_id}"
    retry_job_prefix = f"quiz_retry_{user_id}"

    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        logger.info(f"Removing main job {job.name} for forbidden user {user_id}.")
        job.schedule_removal()

    all_jobs = context.job_queue.jobs() # Get all jobs to find retries
    for job in all_jobs:
        if job.name and job.name.startswith(retry_job_prefix):
            logger.info(f"Removing retry job {job.name} for forbidden user {user_id}.")
            job.schedule_removal()

    if await db_utils.is_user_active_db(user_id):
        await db_utils.remove_active_user_db(user_id)
        logger.info(f"User {user_id} marked as inactive due to Forbidden/Unauthorized error.")

# --- Question Sending Logic (MODIFIED with Caching and direct set usage) ---
async def send_saved_unseen_question(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    global ALL_QUESTIONS_CACHE, last_questions_cache_update
    current_time = time.monotonic()

    if not ALL_QUESTIONS_CACHE or (current_time - last_questions_cache_update > CACHE_MAX_AGE_SECONDS):
        logger.info(f"Updating all_questions_cache from DB (stale or empty). Last update: {last_questions_cache_update}, Now: {current_time}")
        ALL_QUESTIONS_CACHE = await db_utils.get_all_distinct_questions_db()
        last_questions_cache_update = current_time
        logger.info(f"Cache updated with {len(ALL_QUESTIONS_CACHE)} distinct questions.")

    if not ALL_QUESTIONS_CACHE:
        logger.info(f"No system questions in cache for user {user_id} (cache empty after update).")
        return False

    all_system_questions_data = ALL_QUESTIONS_CACHE
    seen_texts_set = await db_utils.get_seen_questions_for_user_db(user_id)
    recent_aspects = await db_utils.get_recent_aspects_for_user_db(user_id, limit=10)
    excluded_chapters = [a.split('\n')[0] for a in recent_aspects if a]

    unseen_questions_data = [
        q_data for q_data in all_system_questions_data 
        if q_data["question"] not in seen_texts_set
        and (not q_data.get("aspect") or q_data["aspect"].split('\n')[0] not in excluded_chapters)
    ]

    if not unseen_questions_data:
        logger.info(f"No unseen questions in database for user {user_id}. Forcing fresh generation.")
        return False

    random.shuffle(unseen_questions_data)
    q_to_send = unseen_questions_data[0]

    try:
        # Split question: Send text message first, then poll
        # Sanitize for HTML parse mode if needed, but the current bot seems to use plain or Markdown?
        # Let's use HTML and escape the text.
        from telegram.helpers import escape_markdown # Already imported as escape_markdown
        # But wait, we want to use bolding for labels.
        
        scenario_text = f"<b>Diagnostic Scenario:</b>\n{html.escape(q_to_send['question'])}"
        await context.bot.send_message(chat_id=chat_id, text=scenario_text, parse_mode=ParseMode.HTML)

        message = await context.bot.send_poll(
            chat_id=chat_id,
            question="Select the best answer below:",
            options=q_to_send["options"],
            type="quiz",
            correct_option_id=q_to_send["correct_index"],
            is_anonymous=False,
        )
        await db_utils.save_poll_data_db(
            poll_id=message.poll.id,
            question=q_to_send["question"],
            options=q_to_send["options"],
            correct_index=q_to_send["correct_index"],
            explanation=q_to_send["explanation"],
            aspect=q_to_send.get("aspect")
        )
        await db_utils.log_event_db('poll_sent', user_id)
        await db_utils.save_quiz_for_user_db(
            user_id=user_id,
            poll_id=message.poll.id,
            question=q_to_send["question"],
            options=q_to_send["options"],
            correct_index=q_to_send["correct_index"],
            explanation=q_to_send["explanation"],
            aspect=q_to_send.get("aspect")
        )
        logger.info(f"Sent saved question to user {user_id}: {q_to_send['question'][:30]}...")
        return True
    except telegram_error.Forbidden as forbidden_err:
        logger.error(f"Telegram Forbidden/Unauthorized error sending saved question to user {user_id}: {forbidden_err}")
        await _handle_forbidden_user(context, user_id)
        return False
    except telegram_error.TelegramError as tg_err:
        logger.error(f"TelegramError sending saved question to user {user_id}: {tg_err}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Generic error sending saved question or saving its data (user {user_id}): {e}", exc_info=True)
        return False

async def send_new_question(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    if not chat_id or not user_id:
        logger.error(f"send_new_question called with missing chat_id ({chat_id}) or user_id ({user_id}).")
        return False

    try:
        if await send_saved_unseen_question(context, chat_id, user_id):
            return True
    except Exception as e_ssuq_wrapper:
        logger.error(f"Unhandled exception from calling send_saved_unseen_question for user {user_id}: {e_ssuq_wrapper}", exc_info=True)

    logger.info(f"Proceeding to generate a new question for user {user_id} (no suitable saved unseen, or issue in saved path).")
    
    recent_aspects = await db_utils.get_recent_aspects_for_user_db(user_id, limit=10)
    excluded_chapters = [a.split('\n')[0] for a in recent_aspects if a]
    
    aspect = get_random_aspect(exclude_chapters=excluded_chapters)
    logger.info(f"Selected aspect for user {user_id} (excluding {len(excluded_chapters)} recent): {aspect.splitlines()[0]}")
    
    # Randomization seeds to force variety
    scenario_styles = ["Straightforward clinical presentation", "Complicated diagnostic dilemma", "Emergency management scenario", "Post-operative complication focus"]
    style = random.choice(scenario_styles)
    random_seed = random.randint(1, 1000)
    
    # NEW: Use system/user prompt split
    user_prompt = EDIC_USER_PROMPT.format(
        aspect=aspect, 
        style=style, 
        question_number=random_seed
    )

    try:
        seen_texts_set = await db_utils.get_seen_questions_for_user_db(user_id)

        async with model_semaphore:
            logger.info(f"Acquired semaphore for user {user_id}. Calling Local Model API...")
            raw_text = await asyncio.to_thread(call_model_sync, EDIC_SYSTEM_PROMPT, user_prompt)
        question, options, correct_index, explanation = parse_question(raw_text)

        if question in seen_texts_set:
            logger.info(f"Duplicate NEW question ('{question[:30]}...') generated and already seen by user {user_id}. Considered a failure for this send attempt.")
            try:
                await context.bot.send_message(chat_id=chat_id, text="I generated a question you've seen recently! I'll try to get a different one next time.")
            except Exception: pass
            return False

        # Split question: Send text message first, then poll
        scenario_text = f"<b>Diagnostic Scenario:</b>\n{html.escape(question)}"
        await context.bot.send_message(chat_id=chat_id, text=scenario_text, parse_mode=ParseMode.HTML)

        message = await context.bot.send_poll(
            chat_id=chat_id,
            question="Select the best answer below:",
            options=options,
            type="quiz",
            correct_option_id=correct_index,
            is_anonymous=False,
        )
        await db_utils.save_poll_data_db(
            poll_id=message.poll.id, question=question, options=options,
            correct_index=correct_index, explanation=explanation, aspect=aspect
        )
        await db_utils.log_event_db('poll_sent', user_id)
        await db_utils.save_quiz_for_user_db(
            user_id=user_id, poll_id=message.poll.id, question=question,
            options=options, correct_index=correct_index, explanation=explanation, aspect=aspect
        )
        # Prune DB to 500 questions
        await db_utils.prune_database_to_limit_db(500)
        
        # Trigger background TikTok video generation
        try:
            from tiktok_video_gen import background_video_task
            asyncio.create_task(background_video_task(question, options, correct_index, explanation))
            logger.info(f"Triggered async TikTok video generation for user {user_id}.")
        except Exception as video_err:
            logger.error(f"Failed to trigger TikTok video generation: {video_err}")
            
        logger.info(f"Sent new question from model to user {user_id}: {question[:30]}...")
        return True

    except ValueError as ve:
        logger.error(f"ValueError in send_new_question (parsing/local model format) for user {user_id}: {ve}", exc_info=False)
        try:
            await context.bot.send_message(chat_id=chat_id, text="Sorry, I had trouble understanding the question format from the local model. Please try `/next` later.")
        except Exception as e_msg: logger.error(f"Failed to send error (ValueError) to user {user_id}: {e_msg}")
        return False
    except TimeoutError as te:
        logger.error(f"TimeoutError calling Local API for user {user_id}: {te}", exc_info=False)
        try:
            await context.bot.send_message(chat_id=chat_id, text="Sorry, the local model timed out. It might be busy or slow. Will retry if scheduled.")
        except Exception as e_msg: logger.error(f"Failed to send error (TimeoutError) to user {user_id}: {e_msg}")
        return False
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTPError calling Local API for user {user_id}: {http_err}", exc_info=False)
        try:
            await context.bot.send_message(chat_id=chat_id, text="Sorry, I'm having trouble connecting to the local model. Will retry if scheduled.")
        except Exception as e_msg: logger.error(f"Failed to send error (HTTPError) to user {user_id}: {e_msg}")
        return False
    except requests.exceptions.RequestException as req_err:
        logger.error(f"RequestException calling Local API for user {user_id}: {req_err}", exc_info=False)
        try:
            await context.bot.send_message(chat_id=chat_id, text="Sorry, I'm having trouble connecting to the local model (network issue). Will retry if scheduled.")
        except Exception as e_msg: logger.error(f"Failed to send error (RequestException) to user {user_id}: {e_msg}")
        return False
    except telegram_error.Forbidden as forbidden_err:
        logger.error(f"Telegram Forbidden/Unauthorized error sending new question to user {user_id}: {forbidden_err}")
        await _handle_forbidden_user(context, user_id)
        return False
    except telegram_error.TelegramError as tg_err:
        logger.error(f"TelegramError during send_poll in send_new_question for user {user_id}: {tg_err}", exc_info=True)
        try:
            await context.bot.send_message(chat_id=chat_id, text="Sorry, there was a Telegram network issue sending your question. Will retry if scheduled.")
        except Exception as e_msg: logger.error(f"Failed to send error (TelegramError) to user {user_id}: {e_msg}")
        return False
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Generic error in send_new_question for user {user_id}: {e}\n{tb}")
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"Oops! Something unexpected went wrong: {str(e)[:50]}")
        except Exception as e_msg: logger.error(f"Failed to send error (Generic Error) to user {user_id}: {e_msg}")
        return False

# --- Job Queue Wrapper for Retries ---
async def attempt_to_send_question_with_retries(context: ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.data:
        logger.error(f"attempt_to_send_question_with_retries called without job or job.data. Job: {context.job}")
        return

    job_data = context.job.data
    chat_id = job_data.get("chat_id")
    user_id = job_data.get("user_id")
    # Use a different key for retries within this chain vs the initial MAX_SEND_RETRIES for a job definition
    retries_left_for_this_instance = job_data.get("retries_left_for_this_instance", MAX_SEND_RETRIES)
    is_retry_job_flag = job_data.get("is_retry_job_flag", False) # Use a more distinct name

    if not chat_id or not user_id:
        logger.error(f"attempt_to_send_question_with_retries: chat_id or user_id missing in job_data. Data: {job_data}")
        return

    job_name_for_log = context.job.name if context.job else 'N/A'
    logger.info(f"Attempting send for user {user_id} (chat_id: {chat_id}). Instance Retries Left: {retries_left_for_this_instance}. Is Retry Job: {is_retry_job_flag}. Job: {job_name_for_log}")

    if not await db_utils.is_user_active_db(user_id):
        logger.info(f"User {user_id} is no longer active. Skipping send attempt for job {job_name_for_log}.")
        # If this is a retry job for an inactive user, ensure the main job is also gone.
        if is_retry_job_flag:
            main_job_name = f"quiz_{user_id}"
            current_main_jobs = context.job_queue.get_jobs_by_name(main_job_name)
            for job_to_remove in current_main_jobs:
                logger.info(f"User {user_id} inactive, removing main repeating job {job_to_remove.name} found during retry processing.")
                job_to_remove.schedule_removal()
        return

    success = await send_new_question(context, chat_id=chat_id, user_id=user_id)

    if success:
        logger.info(f"Successfully sent question to user {user_id}. No further retries needed for this instance (Job: {job_name_for_log}).")
        return

    logger.warning(f"Failed to send question to user {user_id} on this attempt (Job: {job_name_for_log}).")

    if retries_left_for_this_instance > 0:
        next_retry_delay = timedelta(minutes=RETRY_INTERVAL_MINUTES)
        new_retries_left = retries_left_for_this_instance - 1
        retry_job_name = f"quiz_retry_{user_id}_{int(time.time())}"

        context.job_queue.run_once(
            attempt_to_send_question_with_retries,
            when=next_retry_delay,
            data={
                'chat_id': chat_id,
                'user_id': user_id,
                'retries_left_for_this_instance': new_retries_left,
                'is_retry_job_flag': True # Mark as a retry
            },
            name=retry_job_name
        )
        logger.info(f"Scheduled retry for user {user_id} in {RETRY_INTERVAL_MINUTES} min. Retries for this instance: {new_retries_left}. Retry Job: {retry_job_name}")
    else:
        logger.error(f"All {MAX_SEND_RETRIES} retries failed for user {user_id} (chat_id: {chat_id}) for this specific scheduled instance (Original Job: {job_name_for_log}). No more retries for *this* instance.")

# --- Command Handlers (with refined job management) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        logger.warning("/start command received with no effective_chat or effective_user.")
        return
        
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    job_name = f"quiz_{user_id}"

    if await db_utils.is_user_active_db(user_id):
        await update.message.reply_text("You've already started the quiz! Regular questions are scheduled. Use /next for one now, or /stop to pause.")
        if not context.job_queue.get_jobs_by_name(job_name):
            logger.info(f"User {user_id} was active but main job {job_name} missing. Re-scheduling.")
            context.job_queue.run_repeating(
                attempt_to_send_question_with_retries,
                interval=timedelta(hours=6),
                first=timedelta(seconds=random.randint(10, 60)),
                data={'chat_id': chat_id, 'user_id': user_id, 'retries_left_for_this_instance': MAX_SEND_RETRIES, 'is_retry_job_flag': False},
                name=job_name
            )
        return

    await update.message.reply_text("Welcome to MK_ICU_MCQ! I’m sending your first ICU quiz question now. After this, you'll get one every 6 hours. Use /next for more, or /help for commands.")

    initial_send_success = await send_new_question(context, chat_id=chat_id, user_id=user_id)
    if not initial_send_success:
        logger.warning(f"Initial question send failed for user {user_id} during /start. Regular schedule will still attempt.")

    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs: # Remove if any old one exists
        job.schedule_removal()
        logger.info(f"Removed existing job {job_name} for user {user_id} before starting a new one.")

    context.job_queue.run_repeating(
        attempt_to_send_question_with_retries,
        interval=timedelta(hours=6),
        first=timedelta(hours=6), # First scheduled one after initial attempt
        data={'chat_id': chat_id, 'user_id': user_id, 'retries_left_for_this_instance': MAX_SEND_RETRIES, 'is_retry_job_flag': False},
        name=job_name
    )
    await db_utils.add_active_user_db(user_id)
    logger.info(f"User {user_id} started the quiz. Job {job_name} scheduled.")

async def stop_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user:
        logger.warning("/stop command received with no effective_user.")
        return
    user_id = update.effective_user.id
    job_name = f"quiz_{user_id}"
    retry_job_prefix = f"quiz_retry_{user_id}"
    jobs_were_removed = False

    current_main_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_main_jobs:
        job.schedule_removal()
        jobs_were_removed = True
        logger.info(f"Removed main job {job.name} for user {user_id}.")

    all_jobs = context.job_queue.jobs()
    for job in all_jobs:
        if job.name and job.name.startswith(retry_job_prefix):
            job.schedule_removal()
            jobs_were_removed = True
            logger.info(f"Removed retry job {job.name} for user {user_id} during /stop.")

    response_message = "No action taken."
    if await db_utils.is_user_active_db(user_id):
        await db_utils.remove_active_user_db(user_id)
        response_message = "Quiz stopped. You will no longer receive scheduled questions."
        if not jobs_were_removed and not current_main_jobs:
            response_message += " (No active scheduled job was found for you anyway)."
        logger.info(f"User {user_id} stopped the quiz and marked inactive.")
    elif jobs_were_removed:
        response_message = "Your quiz job(s) were removed. You were already marked as not receiving scheduled questions."
    else:
        response_message = "No quiz is currently scheduled for you, and you are marked as inactive."
    
    await update.message.reply_text(response_message + " You can use /start to begin again.")


async def resume_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        logger.warning("/resume command received with no effective_chat or effective_user.")
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    job_name = f"quiz_{user_id}"

    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()
        logger.info(f"Removed existing job {job_name} for user {user_id} before resuming.")

    retry_job_prefix = f"quiz_retry_{user_id}"
    all_jobs = context.job_queue.jobs()
    for job in all_jobs:
        if job.name and job.name.startswith(retry_job_prefix):
            job.schedule_removal()
            logger.info(f"Removed pending retry job {job.name} for user {user_id} during /resume.")

    context.job_queue.run_repeating(
        attempt_to_send_question_with_retries,
        interval=timedelta(hours=6),
        first=timedelta(seconds=random.randint(5, 20)),
        data={'chat_id': chat_id, 'user_id': user_id, 'retries_left_for_this_instance': MAX_SEND_RETRIES, 'is_retry_job_flag': False},
        name=job_name
    )
    if not await db_utils.is_user_active_db(user_id):
        await db_utils.add_active_user_db(user_id)

    await update.message.reply_text("Quiz resumed! You will start receiving questions again shortly. You can also use /next now.")
    logger.info(f"User {user_id} resumed the quiz. Job {job_name} scheduled.")

async def next_question_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        logger.warning("/next command received with no effective_chat or effective_user.")
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Auto-register user if they aren't already
    await db_utils.add_active_user_db(user_id)

    await update.message.reply_text("Fetching your next ICU quiz question... ⏳")
    await db_utils.log_event_db('command_next', user_id)

    if not await send_new_question(context, chat_id=chat_id, user_id=user_id):
        logger.info(f"/next command failed to send question for user {user_id}.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def send_to_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a 'hello' message to all users in the database."""
    # Basic security: you might want to check for admin user_id here
    # if update.effective_user.id != ADMIN_ID: return
    
    user_ids = await db_utils.get_all_user_ids_db()
    total = len(user_ids)
    sent_count = 0
    failed_count = 0

    await update.message.reply_text(f"Starting broadcast to {total} users... 📢")
    
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text="hello message")
            sent_count += 1
            # Small delay to avoid hitting Telegram's rate limits for large lists
            if sent_count % 30 == 0:
                await asyncio.sleep(1)
        except telegram_error.Forbidden:
            logger.warning(f"User {user_id} has blocked the bot. Skipping.")
            failed_count += 1
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")
            failed_count += 1

    await update.message.reply_text(f"Broadcast complete! ✅\nSent: {sent_count}\nFailed/Blocked: {failed_count}")

# --- Poll and Callback Handlers ---
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.poll_answer or not update.poll_answer.user:
        logger.warning("Poll answer received without poll_answer or user data.")
        return
        
    poll_id = update.poll_answer.poll_id
    user_id = update.poll_answer.user.id

    # Auto-register user if they engage with a poll
    await db_utils.add_active_user_db(user_id)

    poll_info = await db_utils.get_poll_data_db(poll_id)

    if poll_info:
        correct_index = poll_info["correct_index"]
        explanation_raw = poll_info["explanation"]
        question_raw = poll_info["question"]
        options = poll_info["options"] # Should be a list from db_utils

        escaped_question = escape_markdown(str(question_raw or ""), version=1)
        escaped_explanation = escape_markdown(str(explanation_raw or ""), version=1)

        chosen_option_id = update.poll_answer.option_ids[0] if update.poll_answer.option_ids else -1
        is_correct = (chosen_option_id == correct_index)

        correct_answer_text_raw = "N/A"
        if isinstance(options, list) and 0 <= correct_index < len(options):
            correct_answer_text_raw = str(options[correct_index] or "")
        else:
            logger.error(f"Correct index {correct_index} out of bounds or options not a list for poll {poll_id}. Options: {options}")

        chosen_answer_text_raw = "N/A"
        if isinstance(options, list) and 0 <= chosen_option_id < len(options):
            chosen_answer_text_raw = str(options[chosen_option_id] or "")

        escaped_correct_answer_text = escape_markdown(correct_answer_text_raw, version=1)
        escaped_chosen_answer_text = escape_markdown(chosen_answer_text_raw, version=1)

        result_text = (
            f"Regarding the question:\n*{escaped_question}*\n\n"
            f"❄️ You chose: _{escaped_chosen_answer_text}_\n\n"
            f"{'✅ Correct!' if is_correct else '❌ Incorrect.'}\n\n"
        )
        if not is_correct:
            result_text += f"🟢 Correct Answer was: *{escaped_correct_answer_text}*\n\n"
        result_text += f"🍔🧊🥤 *Explanation:*\n{escaped_explanation}"

        logger.info(f"User {user_id} answered poll {poll_id}. Correct: {is_correct}")
        # Save the answer to the database for analytics
        await db_utils.save_quiz_for_user_db(
            user_id=user_id,
            poll_id=poll_id,
            question=question_raw,
            options=options,
            correct_index=correct_index,
            explanation=explanation_raw,
            aspect=poll_info.get("aspect"),
            user_answer_index=chosen_option_id
        )
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Next Question", callback_data=f"next_q_{user_id}")]]
        )
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=result_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        except telegram_error.Forbidden:
            logger.warning(f"User {user_id} has blocked the bot. Cannot send poll answer result.")
            await _handle_forbidden_user(context, user_id)
        except Exception as e:
            logger.warning(f"Could not send private message result to user {user_id} for poll {poll_id}: {e}")
    else:
        logger.warning(f"Poll data for poll_id {poll_id} not found in DB. User {user_id} answered an old/unknown poll.")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user:
        logger.warning("Callback query received without query or query.from_user data.")
        return
    user_id = query.from_user.id

    try:
        await query.answer()
    except telegram_error.BadRequest as e:
        if "Query is too old" in str(e):
            logger.warning(f"Callback query {query.id} for user {user_id} is too old to answer.")
        else:
            logger.error(f"BadRequest answering callback query {query.id} for user {user_id}: {e}")
        return
    except Exception as e:
        logger.error(f"Error answering callback query {query.id} for user {user_id}: {e}")
        return

    callback_data = query.data
    if callback_data and callback_data.startswith("next_q_"):
        # For this button, the user_id is the one who pressed it.
        target_user_id = user_id
        logger.info(f"Handling 'Next Question' callback from user {target_user_id}")
        try:
            await context.bot.send_message(chat_id=target_user_id, text="Fetching your next question... ⏳")
        except Exception as e:
            logger.warning(f"Failed to send ack for 'Next Question' callback to user {target_user_id}: {e}")

        await send_new_question(context, chat_id=target_user_id, user_id=target_user_id)

# --- Application Setup and Startup ---
async def on_startup(app: Application):
    await db_utils.init_db()
    logger.info("Database initialized on startup.")

    # Load initial cache for all_system_questions
    global ALL_QUESTIONS_CACHE, last_questions_cache_update
    logger.info("Performing initial population of ALL_QUESTIONS_CACHE on startup...")
    ALL_QUESTIONS_CACHE = await db_utils.get_all_distinct_questions_db()
    last_questions_cache_update = time.monotonic()
    logger.info(f"Initial cache populated with {len(ALL_QUESTIONS_CACHE)} distinct questions.")


    active_user_ids = await db_utils.get_all_active_users_db()
    logger.info(f"Found {len(active_user_ids)} active users in DB to reschedule jobs for.")
    stagger_base = 10
    for user_id_from_db in active_user_ids:
        try:
            chat_id_for_job = user_id_from_db
            job_name = f"quiz_{user_id_from_db}"
            retry_job_prefix = f"quiz_retry_{user_id_from_db}"

            existing_jobs = app.job_queue.get_jobs_by_name(job_name)
            for old_job in existing_jobs:
                old_job.schedule_removal()
                logger.info(f"Removed pre-existing main job {job_name} for user {user_id_from_db} during startup.")

            all_current_jobs = app.job_queue.jobs()
            for current_job_in_queue in all_current_jobs:
                if current_job_in_queue.name and current_job_in_queue.name.startswith(retry_job_prefix):
                    current_job_in_queue.schedule_removal()
                    logger.info(f"Removed pre-existing retry job {current_job_in_queue.name} for user {user_id_from_db} during startup.")

            app.job_queue.run_repeating(
                attempt_to_send_question_with_retries,
                interval=timedelta(hours=6),
                first=timedelta(seconds=random.randint(stagger_base, stagger_base + 60 + len(active_user_ids))), # Stagger startup jobs
                data={'chat_id': chat_id_for_job, 'user_id': user_id_from_db, 'retries_left_for_this_instance': MAX_SEND_RETRIES, 'is_retry_job_flag': False},
                name=job_name
            )
            logger.info(f"Rescheduled quiz job {job_name} for active user {user_id_from_db}.")
            stagger_base += 1 # Slightly increase stagger for next user
        except Exception as e:
            logger.error(f"Failed to reschedule job for user {user_id_from_db}: {e}", exc_info=True)

    # Schedule daily cleanup for old poll data from db_utils
    # Ensure db_utils.cleanup_old_poll_data_db can be called by job_queue
    # (it will receive context as its first arg if it's defined to accept it)
    app.job_queue.run_repeating(
        db_utils.cleanup_old_poll_data_db,
        interval=timedelta(days=1),
        first=timedelta(hours=1), # Run sooner after startup, then daily
        name="daily_poll_cleanup"
    )
    logger.info("Scheduled daily old poll data cleanup job.")

def main() -> None:
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_quiz))
    application.add_handler(CommandHandler("resume", resume_quiz))
    application.add_handler(CommandHandler("next", next_question_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sendall", send_to_all_command))

    application.add_handler(PollAnswerHandler(handle_poll_answer))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    logger.info("Bot starting to poll...")
    application.run_polling()
    logger.info("Bot has stopped.")

if __name__ == "__main__":
    main()
