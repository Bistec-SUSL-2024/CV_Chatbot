import os
import io
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from sentence_transformers import SentenceTransformer
import numpy as np
from pinecone import Pinecone, ServerlessSpec
from sklearn.cluster import AgglomerativeClustering

# Load environment variables
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=creds)

PINECONE_API_KEY = os.getenv("pineconeAPI")
PINECONE_ENVIRONMENT = os.getenv("PineconeEnvironment2")
INDEX_NAME = os.getenv("PineconeIndex2")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT.split("-")[1])
    )

index = pc.Index(INDEX_NAME)

# Sentence Transformer Model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Efficient and fast sentence embedding model

def generate_random_vector(dim=1536):
    return np.random.rand(dim).tolist()

def semantic_chunking(text, threshold=1.5):
    """
    Create semantic chunks using sentence embeddings and hierarchical clustering.
    """
    sentences = text.split('. ')
    embeddings = model.encode(sentences)
    
    # Perform hierarchical clustering
    clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=threshold, linkage='average')
    clustering.fit(embeddings)
    
    chunks = []
    current_chunk = []
    current_cluster = clustering.labels_[0]

    for i, sentence in enumerate(sentences):
        if clustering.labels_[i] == current_cluster:
            current_chunk.append(sentence)
        else:
            chunks.append('. '.join(current_chunk))
            current_chunk = [sentence]
            current_cluster = clustering.labels_[i]

    # Add the last chunk
    if current_chunk:
        chunks.append('. '.join(current_chunk))

    return chunks

FOLDER_ID = '1whaChKzr1JpKV_O7rxkFQJzaNWy2sPKG'

query = f"'{FOLDER_ID}' in parents and mimeType='text/markdown'"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
files = results.get('files', [])

if not files:
    print("No markdown files found in the folder.")
else:
    print(f"Found {len(files)} markdown files.")

    for file in files:
        file_id = file['id']
        file_name = file['name']

        try:
            # Download file
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)
            markdown_text = fh.read().decode('utf-8')
            print(f"Downloaded: {file_name}")

            # Perform semantic chunking
            chunks = semantic_chunking(markdown_text)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_name}_chunk_{i}"
                vector = model.encode(chunk).tolist()
                metadata = {"text": chunk}

                print(f"Chunk {i}:\n{chunk}\n")

                try:
                    upsert_response = index.upsert(vectors=[{
                        "id": chunk_id,
                        "values": vector,
                        "metadata": metadata
                    }])
                    print(f"Upserted chunk: {chunk_id}")
                except Exception as e:
                    print(f"Error during upsert of {chunk_id}: {e}")

        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
