import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
res = client.models.embed_content(
    model='gemini-embedding-2',
    contents='Hello world',
    config=types.EmbedContentConfig(output_dimensionality=768)
)
print("New dimension:", len(res.embeddings[0].values))
