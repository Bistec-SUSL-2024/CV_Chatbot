import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Document,
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
index_name = "testing-01"
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

#------------------------------------Checking data folder----------------------------------------------------------

def rebuild_index():
    if not os.listdir("data"):
        print("Data directory is empty. Index will not be created.")
        return
    
    
    documents = SimpleDirectoryReader("data").load_data()

    
    nodes = []
    for doc in documents:
        vector = embed_model.get_text_embedding(doc.text)
        print(vector)
        node = Node(id_=doc.id_, embedding=vector, metadata={"text": doc.text})
        nodes.append(node)
    
    
    vector_store.add(nodes=nodes)
    
    
    return VectorStoreIndex(nodes=nodes, vector_store=vector_store)


#------------------------------------Query Part--------------------------------------------------------

def query_cv(prompt):
    index = rebuild_index()
    if index is None:
        raise ValueError("Index has not been initialized. Please check the data directory or persisted storage.")

    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    
    return str(response)


prompt = "I have job that needs 2 persons who has skills of python and django. Who are the best among them?"
response = query_cv(prompt)


print("Query Results:", response)


