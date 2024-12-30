import pinecone
from llama_index import VectorStoreIndex, SimpleNode
from llama_index.vector_stores.pinecone import PineconeVectorStore  # Try this path or alternative paths.

# Initialize Pinecone
pinecone.init(api_key="your-pinecone-api-key", environment="your-environment")
index_name = "example-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=768)

pinecone_index = pinecone.Index(index_name)

# Create Pinecone Vector Store
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Example Usage
nodes = [SimpleNode(text="This is a test document.")]
index = VectorStoreIndex(nodes, vector_store=vector_store)
query = "test"
response = index.query(query)
print(response)
