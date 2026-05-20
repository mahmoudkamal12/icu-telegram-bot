import asyncio
import edge_tts

async def dump_chunks():
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate("Testing one two three.", voice)
    
    async for chunk in communicate.stream():
        print("Chunk type:", chunk["type"])
        if chunk["type"] != "audio":
            print(chunk)

asyncio.run(dump_chunks())
