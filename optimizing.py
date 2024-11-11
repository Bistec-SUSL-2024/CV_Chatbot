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
from llama_index.core.vector_stores import VectorStoreQuery

load_dotenv()
OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key


pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "ranking-cv"
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
    documents = SimpleDirectoryReader("data").load_data()
    
    existing_ids = set()
    fetch_response = pinecone_index.fetch(ids=[f"doc_{i}" for i in range(len(documents))])

    
    if fetch_response and 'vectors' in fetch_response:
        existing_ids = set(fetch_response['vectors'].keys())

    
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

    
    all_nodes = []
    for doc_id, doc_data in fetch_response.get('vectors', {}).items():
        if 'values' in doc_data and len(doc_data['values']) == 1536:
            metadata_text = doc_data.get('metadata', {}).get('text', "")
            all_nodes.append(Node(id_=doc_id, embedding=doc_data['values'], metadata={"text": metadata_text}))
    
    if all_nodes:
        index = VectorStoreIndex(nodes=all_nodes, vector_store=vector_store)
        print("Index has been initialized from existing Pinecone data.")
    else:
        print("No valid nodes were found to initialize the index.")



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

prompt = "Given a pool of CVs, I need you to extract the names, email addresses, and contact numbers of the individuals who possess such skills. Please prioritize accuracy and provide the requested information in a concise and accessible format."
try:
    results = query_cv(prompt)
    print("Query results are :", results)
    
except ValueError as e:
    print(e)

