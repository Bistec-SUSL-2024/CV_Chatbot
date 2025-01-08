import os
import numpy as np
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Pinecone API details from environment variables
PINECONE_API_KEY = os.getenv("PineconeCVAnalyzerAPI2")
PINECONE_ENVIRONMENT = os.getenv("PineconeEnvironment2")  # e.g., "aws-us-east-1"
INDEX_NAME = os.getenv("PineconeIndex2")

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check if the index exists, and create it if necessary
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,  # Vector dimension must match the index
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT.split("-")[1])  # Extract region
    )

# Connect to the index
index = pc.Index(INDEX_NAME)

# Generate random vectors of dimension 1536
def generate_random_vector(dim=1536):
    return np.random.rand(dim).tolist()

# Example data to upsert (1536-dimensional vectors)
data_to_upsert = [
    {
        "id": "doc1",
        "values": generate_random_vector(),
        "metadata": {"text": "Example document 1"}
    },
    {
        "id": "doc2",
        "values": generate_random_vector(),
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
query_vector = generate_random_vector()  # Example query vector
try:
    query_response = index.query(vector=query_vector, top_k=2, include_metadata=True)
    print(f"Query response: {query_response}")
except Exception as e:
    print(f"Error during query: {e}")
