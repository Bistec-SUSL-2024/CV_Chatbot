#This file download MD Cvs from google drive and chunk. After chunking upsert to pinecone
#Chunking Method : RecursiveCharacterTextSplitter

import os
import io
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from pinecone import Pinecone, ServerlessSpec

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

pc = Pinecone(api_key=PINECONE_API_KEY)

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT.split("-")[1])
    )

index = pc.Index(INDEX_NAME)

def generate_random_vector(dim=1536):
    return np.random.rand(dim).tolist()

def chunk_text(text, chunk_size=750, overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    return text_splitter.create_documents([text])

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
            
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)
            markdown_text = fh.read().decode('utf-8')
            print(f"Downloaded: {file_name}")
            
            chunks = chunk_text(markdown_text)
          
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_name}_chunk_{i}"
                vector = generate_random_vector()
                metadata = {"text": chunk.page_content}

                print(f"Chunk {i}: {chunk.page_content}\n")

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