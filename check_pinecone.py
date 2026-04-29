import os
import asyncio
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(host=os.environ.get("PINECONE_HOST"))

stats = index.describe_index_stats()
print(stats)
