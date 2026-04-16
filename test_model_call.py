from config import EDIC_SYSTEM_PROMPT, EDIC_USER_PROMPT, API_URL, MODEL_NAME
import requests

user_prompt = EDIC_USER_PROMPT.format(aspect="Chapter 17: End-of-Life Care\nEthical and Legal Principles in End-of-Life Decision Making\nAdvance Directives, Living Wills, and Surrogate Decision-Makers", style="straightforward clinical presentation", question_number="12345")

data = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": EDIC_SYSTEM_PROMPT},
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

try:
    resp = requests.post(API_URL, json=data, timeout=600)
    print("STATUS:", resp.status_code)
    print("OUTPUT:\n", resp.json()["choices"][0]["message"]["content"])
except Exception as e:
    print("ERROR:", e)
