import re
import json

def clean_response(raw_text: str) -> str:
    # 1. Try to find JSON wrapped in ```json ... ``` markdown block
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if json_match:
        try:
            json.loads(json_match.group(1))
            return json_match.group(1).strip()
        except json.JSONDecodeError:
            pass 
            
    # 2. Strip headers
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
            start_idx = raw_text.find('{', start_idx + 1)
            
    return raw_text.strip()

# SAMPLE RAMBLING DATA (What we hope the model eventually outputs)
rambling_output = """
Thinking Process:
I need to talk about ERAS.
Blah blah blah.
{
  "question": "TEST QUESTION",
  "options": ["A", "B", "C", "D"],
  "correct_index": 0,
  "explanation": "Test explanation"
}
"""

cleaned = clean_response(rambling_output)
print("CLEANED OUTPUT:")
print(cleaned)

try:
    data = json.loads(cleaned)
    print("SUCCESS: JSON is valid!")
except Exception as e:
    print(f"FAILED: {e}")
