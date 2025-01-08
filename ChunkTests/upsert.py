import pinecone
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Pinecone API details from environment variables
PINECONE_API_KEY = os.getenv("PineconeCVAnalyzerAPI2")
PINECONE_ENVIRONMENT = os.getenv("PineconeEnvironment2")  # Fixed environment variable key
INDEX_NAME = os.getenv("PineconeIndex2")

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Check if the index exists, if not, create it
if INDEX_NAME not in pinecone.list_indexes():
    pinecone.create_index(name=INDEX_NAME, dimension=1536, metric="cosine")

# Connect to the index
index = pinecone.GRPCIndex(INDEX_NAME)  # Updated to use GRPCIndex

# Example data to upsert
data_to_upsert = [
    {
        "id": "doc1",  # Unique ID for the vector
        "values": [0.1, 0.2, 0.3, 0.4],  # Vector values (must match the dimension of the index)
        "metadata": {"text": "Example document 1"}
    },
    {
        "id": "doc2",
        "values": [0.5, 0.6, 0.7, 0.8],
        "metadata": {"text": "Example document 2"}
    }
]

# Upsert data into the index
try:
    upsert_response = index.upsert(vectors=data_to_upsert)
    print(f"Upsert response: {upsert_response}")
except Exception as e:
    print(f"Error during upsert: {e}")

# Query example (optional)
query_vector = [0.1, 0.2, 0.3, 0.4]  # Example query vector
try:
    query_response = index.query(vector=query_vector, top_k=2, include_metadata=True)
    print(f"Query response: {query_response}")
except Exception as e:
    print(f"Error during query: {e}")
