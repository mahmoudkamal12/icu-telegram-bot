# config.example.py
# Copy this file to config.py and fill in your details

API_KEY = "not-needed-for-local"
API_URL = "http://192.168.1.7:1234/v1/chat/completions"
# Updating to use Gemma 3 4B or Qwen 2.5 Coder which are usually much more stable
MODEL_NAME = "qwen/qwen3.5-9b"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

EDIC_SYSTEM_PROMPT = (
    "You are a world-class ICU Consultant. Respond ONLY with a valid JSON object. "
    # ... rest of system prompt
)

EDIC_USER_PROMPT = (
    "Generate a new question on the following:\n"
    "Topic: {aspect}\n"
    "Style/Context: {style}\n"
    "Seed ID: {question_number}\n\n"
    "Respond ONLY with valid JSON."
)

help_text = (
        "Welcome to MK_ICU_MCQ!\n\n"
        "Need more help? Contact the admin: @your_username\n"
        "/start - Start the quiz and get your first question\n"
        "/next - Get the next question immediately\n"
        "/stop - Stop receiving questions\n"
        "/resume - Resume the quiz\n"
        "/help - Show this help message"
)
