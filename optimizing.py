import os
import numpy as np
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
)
from llama_index.core.schema import Node
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv


load_dotenv()
OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key


pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "llama-integration-example"
if index_name not in pc.list_indexes().names():
    
    pc.create_index(
        name=index_name,
        dimension=1536,  
        metric='cosine',
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
pinecone_index = pc.Index(index_name)


vector_store = PineconeVectorStore(pinecone_index=pinecone_index)


embed_model = OpenAIEmbedding()

index = None

#----------------------------------Creating Vectors of Documents-----------------------------------------

def rebuild_index():
    global index

    
    if not os.listdir("data"):
        print("Data directory is empty. Index will not be created.")
        return

    documents = SimpleDirectoryReader("data").load_data()

    existing_ids = set(item['id'] for item in pinecone_index.query(vector=[0]*1536, top_k=len(documents)).matches)

    nodes = []
    for i, doc in enumerate(documents):
        doc_id = f"doc_{i}"
        if doc_id not in existing_ids:
            vector = embed_model.get_text_embedding(doc.text)
            if vector is None or len(vector) != 1536:
                print(f"Skipping document {doc_id} due to invalid embedding.")
                continue

            node = Node(id_=doc_id, embedding=vector, metadata={"text": doc.text})
            nodes.append(node)
        else:
            print(f"Document {doc_id} is already in Pinecone index, skipping.")

    
    if nodes:
        vector_store.add(nodes=nodes)
        print("New documents have been embedded and stored in the Pinecone index.")
        
        index = VectorStoreIndex(nodes=nodes, vector_store=vector_store)
    else:
        # Load existing nodes into the index if no new documents were added
        existing_nodes = [
            Node(id_=match['id'], embedding=match['values'], metadata={"text": match.get('metadata', {}).get('text', "")})
            for match in pinecone_index.query(vector=[0]*1536, top_k=len(documents)).matches
            if 'values' in match and len(match['values']) == 1536  # Ensure only non-empty embeddings
        ]
        if existing_nodes:
            index = VectorStoreIndex(nodes=existing_nodes, vector_store=vector_store)
        print("All documents are already stored in the Pinecone index.")



#-------------------------------------------Create Vectors of Query------------------------------------------------------



def query_cv(prompt):
    global index

    if index is None:
        raise ValueError("Index has not been initialized. Please check the data directory or persisted storage.")

    query_embedding = embed_model.get_text_embedding(prompt)
    if query_embedding is None or len(query_embedding) != 1536:
        raise ValueError("Query embedding is empty or invalid.")

    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)

    return response


rebuild_index()

prompt = "What are the contact numbers and emails of the owner of CV's?"
try:
    results = query_cv(prompt)
    print("Query Results:", results)
except ValueError as e:
    print(e)
