import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core.schema import Node
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

# Initialize Pinecone
pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "llama-integration-example"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Adjust based on the embedding model
        metric='cosine',
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
pinecone_index = pc.Index(index_name)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Initialize embedding model
embed_model = OpenAIEmbedding()

# Step 1: Store Embeddings in Pinecone
def store_embeddings():
    documents = SimpleDirectoryReader("data").load_data()
    
    for i, doc in enumerate(documents):
        # Check if document is already in Pinecone
        result = pinecone_index.query(vector=embed_model.get_text_embedding(doc.text), top_k=1, include_metadata=True)
        
        if result['matches'] and result['matches'][0]['metadata'].get('text') == doc.text:
            print(f"Document doc_{i} is already in Pinecone index, skipping.")
            continue
        
        # Create embedding and store if not already present
        vector = embed_model.get_text_embedding(doc.text)
        pinecone_index.upsert([{
            "id": f"doc_{i}",
            "values": vector,
            "metadata": {"text": doc.text}
        }])
        print(f"Document doc_{i} has been embedded and stored in Pinecone index.")

# Step 2: Query Pinecone for Relevant Documents
def query_documents(prompt):
    embedding = embed_model.get_text_embedding(prompt)
    results = pinecone_index.query(vector=embedding, top_k=3, include_metadata=True)

    for match in results['matches']:
        print(f"Match: {match['metadata']['text']}, Score: {match['score']}")

# Run storage and query functions
store_embeddings()

# Example Query
prompt = "Provide me the name and contact number of the owner of this cv?."
query_documents(prompt)
