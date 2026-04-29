import os
from google import genai
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
res = client.models.embed_content(
    model='gemini-embedding-2',
    contents='Hello world'
)
print("Dimension of gemini-embedding-2:", len(res.embeddings[0].values))
