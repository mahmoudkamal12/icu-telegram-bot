import re

text = """Diagnostic Scenario:

A 65-year-old male presents with acute shortness of breath and chest pain. ECG shows ST elevation in V1-V4.

Options:
A. Administer Aspirin
B. Perform PCI
C. Give Nitroglycerin
D. Give Beta Blockers"""

def split_into_chunks(text):
    chunks = []
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        # Split by sentence endings, keep the punctuation
        sentences = re.split(r'(?<=[.!?]) +', line)
        for s in sentences:
            if s.strip():
                chunks.append(s.strip())
    return chunks

for i, c in enumerate(split_into_chunks(text)):
    print(f"Chunk {i}: {c}")
