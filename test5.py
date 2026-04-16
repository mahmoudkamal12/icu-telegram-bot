"""
5-Question Test: Run until ALL 5 pass. Logs everything to test5_results.txt
"""
import requests
import re
import random
import sys

# --- Load config directly to avoid import issues ---
sys.path.insert(0, r"d:\icu telegram bot\last version\coding")
from config import EDIC_SYSTEM_PROMPT, EDIC_USER_PROMPT, API_URL, MODEL_NAME

ASPECTS = [
    "Septic Shock Management",
    "ARDS Management",
    "Mechanical Ventilation Weaning",
    "Acute Kidney Injury in ICU",
    "Neurological Emergencies in ICU",
]

LOG_FILE = r"d:\icu telegram bot\last version\coding\test5_results.txt"

def call_model(system_prompt, user_prompt):
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 3000,
    }
    resp = requests.post(API_URL, json=data, timeout=600)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def clean_response(raw_text):
    text = raw_text
    # Try to find </think> or </thought>
    think_end = re.search(r"</(?:think|thought)>", text, re.IGNORECASE)
    if think_end:
        text = text[think_end.end():].strip()
    else:
        # Remove any <think>...</think> blocks
        text = re.sub(r"<(?:think|thought)>.*?</(?:think|thought)>", "", text, flags=re.IGNORECASE | re.DOTALL)
        # Find first Q: marker
        q_match = re.search(r"(?:^|\n)\s*(?:\*\*)?Q\s*[:\-]", text, re.IGNORECASE)
        if q_match:
            text = text[q_match.start():].strip()
    return text.replace('–', '-').replace('—', '-').strip()

def parse_question(raw_text):
    text = clean_response(raw_text)
    
    # Question
    q_match = re.search(
        r"(?:\*\*|)\s*Q\s*(?:\*\*|)\s*[:\-]\s*(.*?)(?=\n\s*(?:\*\*|)\s*[A-D][).:\-\s])",
        text, re.IGNORECASE | re.DOTALL
    )
    # Options A-D
    opts_raw = re.findall(
        r"^(?:\*\*|)\s*([A-D])[).:\-\s\*]+\s*(.*?)(?=\n(?:\*\*|)\s*[A-D][).:\-\s]|\n(?:Correct Answer|Answer)|$)",
        text, re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    # Answer
    ans_match = re.search(r"(?:Correct Answer|Answer)\s*[:\-]?\s*(?:\*\*|)\s*([A-D])", text, re.IGNORECASE)
    # Explanation
    expl_match = re.search(r"Explanation\s*[:\-]?\s*(.*)", text, re.IGNORECASE | re.DOTALL)

    return text, q_match, opts_raw, ans_match, expl_match

def main():
    results = []
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for i, aspect in enumerate(ASPECTS):
            seed = random.randint(1, 999)
            print(f"\n=== Test {i+1}/5: {aspect} (seed={seed}) ===")
            f.write(f"\n{'='*60}\n=== Test {i+1}/5: {aspect} (seed={seed}) ===\n{'='*60}\n")
            
            user_prompt = EDIC_USER_PROMPT.format(aspect=aspect, style="Clinical Scenario", question_number=seed)
            try:
                raw = call_model(EDIC_SYSTEM_PROMPT, user_prompt)
                f.write(f"\n--- RAW OUTPUT ---\n{raw}\n--- END RAW ---\n")
                
                cleaned, q_m, opts, ans_m, expl_m = parse_question(raw)
                f.write(f"\n--- CLEANED ---\n{cleaned[:500]}\n--- /CLEANED ---\n")
                
                ok = bool(q_m and opts and ans_m)
                results.append(ok)
                
                status = "✅ PASS" if ok else "❌ FAIL"
                details = f"Q={bool(q_m)}, Opts={len(opts)}, Ans={bool(ans_m)}"
                msg = f"{status} | {details}"
                print(msg)
                f.write(f"\nRESULT: {msg}\n")
                
                if ok:
                    q = q_m.group(1).strip()[:120]
                    opts_list = {o[0]: o[1].strip() for o in opts}
                    correct = ans_m.group(1)
                    print(f"  Q: {q}...")
                    print(f"  Correct: {correct}")
                    f.write(f"Q: {q}\nCorrect: {correct}\n")
                    for opt_letter in ["A","B","C","D"]:
                        print(f"  {opt_letter}. {opts_list.get(opt_letter,'??')}")
                    
            except Exception as e:
                print(f"ERROR: {e}")
                f.write(f"\nERROR: {e}\n")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        summary = f"\n{'='*60}\nFINAL: {passed}/{total} PASSED\n{'='*60}"
        print(summary)
        f.write(summary + "\n")

if __name__ == "__main__":
    main()
