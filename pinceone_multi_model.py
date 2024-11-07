import os
import time
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv
from PyPDF2 import PdfReader

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)


index_name = "testing-pine-model"
namespace = "example-namespace"
embedding_dimension = 1024  


if index_name in pc.list_indexes().names():
    index_info = pc.describe_index(index_name)
    if index_info['dimension'] != embedding_dimension:
        pc.delete_index(index_name)
        print(f"Index '{index_name}' with incorrect dimension deleted.")

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,  
        metric='cosine',
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Index '{index_name}' has been created with dimension {embedding_dimension}.")


index = pc.Index(index_name)

#---------------------------------Function to retrieve all IDs from the index in a specific namespace-----------------------------------

def get_existing_ids():
    existing_ids = set()
    response = index.query(
        vector=[0] * embedding_dimension,  
        namespace=namespace,
        top_k=10,
        include_metadata=False
    )
    for match in response['matches']:
        existing_ids.add(match['id'])
    return existing_ids


stored_ids = get_existing_ids()
print("Existing IDs in index:", stored_ids)

pdf_directory = "./data"

data = []
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        file_id = filename.replace(".pdf", "")
        if file_id not in stored_ids: 
            filepath = os.path.join(pdf_directory, filename)
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            data.append({"id": file_id, "text": text})

if data:

    embeddings = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[d['text'] for d in data],
        parameters={"input_type": "passage", "truncate": "END"}
    )

    print("Embeddings have been created....")

    records = [{"id": d['id'], "values": e['values'], "metadata": {"text": d['text']}} for d, e in zip(data, embeddings)]

    index.upsert(
        vectors=records,
        namespace=namespace
    )
    print("New records have been stored in index....")
else:
    print("No new embeddings to add. All PDFs are already stored in the index.")


#----------------------------------Function to query the index based on a user query-------------------------------------------------


def query_index(query_text, top_k=5):
    query_embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query_text],
        parameters={"input_type": "passage", "truncate": "END"}
    )[0]['values']  
    
    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace=namespace,
        include_metadata=True
    )

    
    results = []
    for match in response['matches']:
        match_id = match['id']
        match_score = match['score']
        match_text = match['metadata']['text']
        results.append((match_id, match_score, match_text))

    return results


user_query = "I have a job that needs experience of project management. Provide me names who has these skills??"
query_results = query_index(user_query)


print("Query results:")
for idx, (match_id, score, text) in enumerate(query_results, start=1):
    print(f"\nResult {idx}:")
    print(f"Score: {score}")
    print(f"Text: {text[:500]}...") 
