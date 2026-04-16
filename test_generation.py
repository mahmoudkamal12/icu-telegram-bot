import requests
import re
import random
import html
from config import EDIC_SYSTEM_PROMPT, EDIC_USER_PROMPT, API_URL, MODEL_NAME

def call_model_sync(system_prompt: str, user_prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 3000
    }
    resp = requests.post(API_URL, headers=headers, json=data, timeout=600)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def clean_response(raw_text: str) -> str:
    text = raw_text
    # Strategy 1: Find thinking end tag
    think_end = re.search(r"</(?:think|thought)>", text, re.IGNORECASE)
    if think_end:
        text = text[think_end.end():].strip()
    else:
        # Strategy 2: Strip full tags if they exist but no end tag was found (unlikely but safe)
        text = re.sub(r"<(?:think|thought)>.*?</(?:think|thought)>", "", text, flags=re.IGNORECASE | re.DOTALL)
        # Strategy 3: Fallback - find first Q: or Question identifier
        markers = [
            r"(?:^|\n)\s*(?:\*\*)?Q\s*[:\-]",
            r"(?:^|\n)\s*(?:\*\*)?Question\s*[:\-]",
            r"(?:^|\n)\s*(?:\*\*)?Diagnostic Scenario\s*[:\-]"
        ]
        earliest_pos = -1
        for marker in markers:
            m = re.search(marker, text, re.IGNORECASE)
            if m:
                if earliest_pos == -1 or m.start() < earliest_pos:
                    earliest_pos = m.start()
        if earliest_pos != -1:
            text = text[earliest_pos:].strip()
            
    return text.replace('–', '-').replace('—', '-').strip()

def parse_question(raw_text: str):
    text = clean_response(raw_text)
    # Match Question
    question_match = re.search(
        r"(?:\*\*|)\s*(?:Q(?:uiz Question|uestion|uiz)?|Diagnostic Scenario|Case Scenario)\s*(?:\*\*|)\s*[:-]\s*(.*?)(?=\n(?:\*\*|)\s*[A-D][).:\-\s])", 
        text, re.IGNORECASE | re.DOTALL
    )
    # Match Options A-D
    options_raw = re.findall(
        r"^(?:\*\*|)\s*([A-D])[).:\-\s\*]+\s*(.*?)(?=\n(?:\*\*|)\s*[A-D][).:\-\s]|\n(?:Correct Answer|Answer)|$)", 
        text, re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    # Match Correct Answer
    answer_match = re.search(r"(?:Correct Answer|Answer)\s*[:-]?\s*(?:\*\*|)\s*([A-D])", text, re.IGNORECASE)
    # Match Explanation
    explanation_match = re.search(r"Explanation\s*[:-]?\s*(.*)", text, re.IGNORECASE | re.DOTALL)

    if not (question_match and options_raw and answer_match):
        print(f"FAILED: q={bool(question_match)}, opts={len(options_raw)}, a={bool(answer_match)}")
        return None

    question = question_match.group(1).strip()
    options_dict = {opt[0].upper(): opt[1].strip() for opt in options_raw}
    options = [options_dict.get(letter, "") for letter in ['A', 'B', 'C', 'D']]
    
    correct_letter = answer_match.group(1).upper()
    correct_index = ord(correct_letter) - ord('A')
    explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."
    
    return question, options, correct_index, explanation

def main():
    aspects = ["Sepsis Bundle Priority", "ARDS Management", "Mechanical Ventilation"]
    for i, aspect in enumerate(aspects):
        print(f"\n--- Testing Question {i+1}: {aspect} ---")
        user_prompt = EDIC_USER_PROMPT.format(aspect=aspect, style="Clinical Scenario", question_number=random.randint(1, 999))
        try:
            raw_text = call_model_sync(EDIC_SYSTEM_PROMPT, user_prompt)
            print("RAW (first 100 chars):", raw_text[:100].replace('\n', ' '))
            print("-" * 40)
            parsed = parse_question(raw_text)
            if parsed:
                q, opts, ans_idx, expl = parsed
                print("✅ PARSED SUCCESSFULLY!")
                print(f"Q: {q[:100]}...")
            else:
                print("❌ FAILED TO PARSE.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
