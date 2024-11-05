import os
import time
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)


data = [
    {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
    {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
    {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
    {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
    {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
    {"id": "vec6", "text": "Apple Computer Company was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne as a partnership."}
]


embeddings = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[d['text'] for d in data],
    parameters={"input_type": "passage", "truncate": "END"}
)

# print(embeddings)
print("Embeddings have been created....")

# -----------------------------------------Creating Index-----------------------------------------


# index_name = "example-index"

# pc.create_index(
#     name=index_name,
#     dimension=1024,
#     metric="cosine",
#     spec=ServerlessSpec(
#         cloud='aws', 
#         region='us-east-1'
#     ) 
# ) 

# # Wait for the index to be ready
# while not pc.describe_index(index_name).status['ready']:
#     time.sleep(1)

# print("Index has been created....")


#---------------------Stroing vectors in Index--------------------------------



index = pc.Index("example-index")

# Prepare the records for upsert
# Each contains an 'id', the embedding 'values', and the original text as 'metadata'
records = []
for d, e in zip(data, embeddings):
    records.append({
        "id": d['id'],
        "values": e['values'],
        "metadata": {'text': d['text']}
    })

# Upsert the records into the index
index.upsert(
    vectors=records,
    namespace="example-namespace"
)


print("Records have been stored in index....")

#---------------------------------------------------------------------------------------------------



time.sleep(4)  # Wait for the upserted vectors to be indexed

# print(index.describe_index_stats())


#---------------------------------------------------------------------------------------------------

# Define your query
query = "Tell me about the tech company known as Apple."

# Convert the query into a numerical vector that Pinecone can search with
query_embedding = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[query],
    parameters={
        "input_type": "query"
    }
)

# Search the index for the three most similar vectors
results = index.query(
    namespace="example-namespace",
    vector=query_embedding[0].values,
    top_k=3,
    include_values=False,
    include_metadata=True
)

# print(results)

print("Anwers are: ")
for match in results['matches']:
    text = match['metadata']['text']
    score = match['score']
    print(f"Text: {text}\nScore: {score}\n")