import os
import random
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

try:
    print("Initializing Pinecone client...")
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    index = pc.Index("synapseip")
    
    print("Checking index stats...")
    stats = index.describe_index_stats()
    print("Stats:", stats)
    
    dim = stats.get("dimension", 3072)
    print(f"Index dimension is {dim}. Generating dummy vector...")
    
    dummy_vector = [random.random() for _ in range(dim)]
    dummy_id = "test_connection_vector"
    
    print("Testing UPSERT...")
    index.upsert(vectors=[(dummy_id, dummy_vector, {"test_key": "test_val"})], namespace="test_namespace")
    print("Upsert successful!")
    
    print("Testing QUERY...")
    query_res = index.query(vector=dummy_vector, top_k=1, namespace="test_namespace")
    print("Query successful. Matches:", [m['id'] for m in query_res.get('matches', [])])
    
    print("Testing DELETE...")
    index.delete(ids=[dummy_id], namespace="test_namespace")
    print("Delete successful!")
    
    print("\n✅ All Pinecone operations completed successfully. Connection is stable.")

except Exception as e:
    print("\n❌ Pinecone connection test failed:", str(e))

