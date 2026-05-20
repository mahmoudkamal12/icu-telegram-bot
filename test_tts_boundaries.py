import asyncio
import edge_tts

async def test_voices():
    voices = ["en-US-JennyNeural", "en-GB-SoniaNeural", "en-AU-NatashaNeural", "en-US-EricNeural", "en-US-SteffanNeural"]
    text = "Hello world, this is a test to see if word boundaries work."
    
    for v in voices:
        print(f"Testing {v}...")
        communicate = edge_tts.Communicate(text, v)
        count = 0
        async for chunk in communicate.stream():
            if chunk["type"] == "WordBoundary":
                count += 1
        print(f"Voice {v}: {count} boundaries")

asyncio.run(test_voices())
