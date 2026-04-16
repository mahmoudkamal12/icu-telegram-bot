import requests
import json
from config import API_URL, MODEL_NAME, EDIC_SYSTEM_PROMPT, EDIC_USER_PROMPT

def test_raw():
    user_prompt = EDIC_USER_PROMPT.format(aspect="Sepsis", style="Emergency", question_number=42)
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": EDIC_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }
    print(f"Connecting to {API_URL}...")
    print(f"Requesting model: {MODEL_NAME}")
    try:
        resp = requests.post(API_URL, json=data, timeout=300)
        resp.raise_for_status()
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        print("\n--- RAW RESPONSE ---")
        print(content)
        print("--- END RESPONSE ---")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    test_raw()
