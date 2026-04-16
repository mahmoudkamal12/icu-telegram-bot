from telegram_bot import parse_question

def test_parse_logic():
    print("--- STARTING TEST ---")
    
    with open("debug_llm.txt", "r", encoding="utf-8") as f:
        real_failure_text = f.read()

    # 1. Normal JSON Output
    normal_json = """
    {
        "question": "What is the capital of France?",
        "options": [
            "London",
            "Berlin",
            "Paris",
            "Madrid"
        ],
        "correct_index": 2,
        "explanation": "Paris is the capital of France."
    }
    """
    
    # 2. JSON enclosed in markdown code block
    markdown_json = """
    Here is the question you requested:
    ```json
    {
        "question": "Which of the following is a symptom of sepsis?",
        "options": [
            "Bradycardia",
            "Hypothermia or hyperthermia",
            "Hypertension",
            "Polycythemia"
        ],
        "correct_index": 1,
        "explanation": "Temperature abnormalities are a hallmark of sepsis."
    }
    ```
    Good luck!
    """

    # 3. Model Output with Hallucinated Braces (The Exact Failure Case)
    exact_failure_json = real_failure_text

    tests = {
        "Normal JSON": normal_json,
        "Markdown Code Block JSON": markdown_json,
        "Real Failure File": exact_failure_json
    }

    for name, raw_text in tests.items():
        print(f"--- Testing: {name} ---")
        try:
            q, o, c, e = parse_question(raw_text)
            print(f"SUCCESS: {q[:40]}...")
            print(f"Options: {o}")
            print(f"Correct: {c} -> {o[c]}")
            print(f"Explain: {e[:40]}...\n")
        except Exception as ex:
            print(f"FAILED: {ex}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_parse_logic()
