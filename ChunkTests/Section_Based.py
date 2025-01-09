#Section Based Chunking

import os
import io
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import re
import numpy as np
from pinecone import Pinecone, ServerlessSpec

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

# Initialize Pinecone instance
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check and create the index if necessary
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT.split("-")[1])
    )

index = pc.Index(INDEX_NAME)

# Function to generate random vectors (for placeholder embeddings)
def generate_random_vector(dim=1536):
    return np.random.rand(dim).tolist()

# Function to chunk text based on sections (e.g., Markdown headers)
def chunk_text_by_sections(text):
    # This regular expression matches headers in Markdown (e.g., '# Section Title')
    section_pattern = r'(^|\n)(#{1,6})\s*(.*?)(?=\n|$)'
    
    # Find all sections (headers)
    sections = re.split(section_pattern, text)
    
    chunks = []
    current_chunk = ""
    for section in sections:
        if section.startswith("#"):  # This is a header, start a new section
            if current_chunk:  # If there's existing content in the chunk, save it
                chunks.append(current_chunk.strip())
            current_chunk = section  # Start a new chunk with the header
        else:
            current_chunk += section  # Add content to the current chunk
    
    if current_chunk:
        chunks.append(current_chunk.strip())  # Append any remaining content
    
    return chunks

# Google Drive folder ID containing markdown files
FOLDER_ID = '1whaChKzr1JpKV_O7rxkFQJzaNWy2sPKG'

# Fetch markdown files from Google Drive
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
            # Download the file content
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)
            markdown_text = fh.read().decode('utf-8')
            print(f"Downloaded: {file_name}")

            # Chunk the text by sections
            chunks = chunk_text_by_sections(markdown_text)

            # Process each chunk
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_name}_chunk_{i}"
                vector = generate_random_vector()
                metadata = {"text": chunk}

                print(f"Chunk {i}: {chunk[:100]}...")  # Print the first 100 chars for preview

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
