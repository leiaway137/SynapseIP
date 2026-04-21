import os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
result = client.models.embed_content(
    model="text-embedding-004",
    contents="Hello world",
)
print("Dimensions:", len(result.embeddings[0].values))
