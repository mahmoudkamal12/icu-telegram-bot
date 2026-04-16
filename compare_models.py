import requests
import re

API_URL = "http://192.168.1.7:1234/v1/chat/completions"

def call_model_sync(model_id: str, topic: str) -> str:
    headers = {"Content-Type": "application/json"}
    detailed_prompt = f"""You are an expert Intensive Care Unit (ICU) physician. Your task is to generate ONE single valid multiple-choice question on the given topic.
Do NOT write any introduction, reasoning, or "Here is the question". 
Strictly follow this structure:
Q: [Detailed clinical Case Scenario]
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
Correct Answer: [Letter]
Explanation: [Explain clearly in simple words why the correct answer is the best choice AND explicitly explain why each of the other three options is incorrect. Use bullet points and emojis.]

Now, generate a new question:
Topic: {topic}"""

    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": detailed_prompt}],
        "temperature": 0.1,
    }
    
    resp = requests.post(API_URL, headers=headers, json=data, timeout=300)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def main():
    topic = "Management of Mixed Acid-Base Disorders in the ICU"
    
    # Test Llama
    print("Generating Llama output...")
    llama_out = call_model_sync("meta-llama-3.1-8b-instruct", topic)
    with open("compare_llama.txt", "w", encoding="utf-8") as f:
        f.write(llama_out)
        
    # Test Nemotron
    print("Generating Nemotron output...")
    nemotron_out = call_model_sync("nvidia/nemotron-3-nano-4b", topic)
    with open("compare_nemotron.txt", "w", encoding="utf-8") as f:
        f.write(nemotron_out)

    print("Done! Check compare_llama.txt and compare_nemotron.txt")

if __name__ == '__main__':
    main()
