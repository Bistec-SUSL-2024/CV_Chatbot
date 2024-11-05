import os
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv


load_dotenv()
OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")


os.environ["OPENAI_API_KEY"] = OpenAI_Key


pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "llama-integration-example"


if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

pinecone_index = pc.Index(index_name)

embed_model = OpenAIEmbedding()

#-------------------------------------Document Indexing------------------------------------------------

documents = SimpleDirectoryReader("data").load_data()
for i, doc in enumerate(documents):

    vector = embed_model.get_text_embedding(doc.text)
    pinecone_index.upsert([
        {
            "id": f"doc_{i}",  
            "values": vector,
            "metadata": {"text": doc.text}
        }
    ])
print("Documents have been embedded and stored in the Pinecone index.")

#----------------------------------------Query_Indexing------------------------------------------------

def query_pinecone_index(query_text):
    
    query_vector = embed_model.get_text_embedding(query_text)
    response = pinecone_index.query(
        vector=query_vector,
        top_k=3,  
        include_metadata=True  
    )
    
    print("Raw Response:", response)

    print("Query Results:")
    for match in response['matches']:
        print("Text:", match['metadata']['text'])
        print("Score:", match['score'])
        print("----------")


query_text = "Provide me information about documents?"
query_pinecone_index(query_text)
