import asyncio
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

async def main():
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        print("Client initialized.")
        res = await client.aio.models.embed_content(
            model='gemini-embedding-2',
            contents="hello world"
        )
        print("Embedding generated! Dimensions:", len(res.embeddings[0].values))
    except Exception as e:
        print("Error:", type(e).__name__, e)

if __name__ == "__main__":
    asyncio.run(main())
