import os
import io
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
from pinecone import Pinecone, ServerlessSpec
from pdfminer.high_level import extract_text

# Load environment variables
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Initialize Google Drive service
drive_service = build('drive', 'v3', credentials=creds)

# Pinecone configuration
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

# Function to generate random vectors
def generate_random_vector(dim=1536):
    return np.random.rand(dim).tolist()

# Function to chunk text
def chunk_text(text, chunk_size=750, overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    return text_splitter.create_documents([text])

# PDF to Markdown conversion
PDF_FOLDER_ID = '1HKDYBXEcE_QbYf5l9p2rDaBXGZk5BDc4'
MARKDOWN_FOLDER_ID = '1whaChKzr1JpKV_O7rxkFQJzaNWy2sPKG'

pdf_query = f"'{PDF_FOLDER_ID}' in parents and mimeType='application/pdf'"
pdf_results = drive_service.files().list(q=pdf_query, fields="files(id, name)").execute()
pdf_files = pdf_results.get('files', [])

if not pdf_files:
    print("No PDF files found in the folder.")
else:
    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:
        pdf_file_id = pdf_file['id']
        pdf_file_name = pdf_file['name']

        try:
            # Download PDF
            request = drive_service.files().get_media(fileId=pdf_file_id)
            pdf_fh = io.BytesIO()
            downloader = MediaIoBaseDownload(pdf_fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            pdf_fh.seek(0)
            pdf_text = extract_text(pdf_fh)
            markdown_content = f"# {pdf_file_name}\n\n" + pdf_text

            # Save as Markdown in the target folder
            markdown_file_name = pdf_file_name.replace('.pdf', '.md')
            markdown_file_path = f"/tmp/{markdown_file_name}"
            with open(markdown_file_path, 'w') as md_file:
                md_file.write(markdown_content)

            file_metadata = {
                'name': markdown_file_name,
                'parents': [MARKDOWN_FOLDER_ID]
            }
            media = MediaFileUpload(markdown_file_path, mimetype='text/markdown')
            drive_service.files().create(body=file_metadata, media_body=media).execute()

            print(f"Converted and uploaded: {markdown_file_name}")

        except Exception as e:
            print(f"Error processing PDF {pdf_file_name}: {e}")

# Process Markdown files
markdown_query = f"'{MARKDOWN_FOLDER_ID}' in parents and mimeType='text/markdown'"
markdown_results = drive_service.files().list(q=markdown_query, fields="files(id, name)").execute()
markdown_files = markdown_results.get('files', [])

if not markdown_files:
    print("No Markdown files found in the folder.")
else:
    print(f"Found {len(markdown_files)} Markdown files.")

    for md_file in markdown_files:
        md_file_id = md_file['id']
        md_file_name = md_file['name']

        try:
            # Download Markdown
            request = drive_service.files().get_media(fileId=md_file_id)
            md_fh = io.BytesIO()
            downloader = MediaIoBaseDownload(md_fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            md_fh.seek(0)
            markdown_text = md_fh.read().decode('utf-8')

            # Chunk and upsert to Pinecone
            chunks = chunk_text(markdown_text)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{md_file_name}_chunk_{i}"
                vector = generate_random_vector()
                metadata = {"text": chunk.page_content}

                try:
                    index.upsert(vectors=[{
                        "id": chunk_id,
                        "values": vector,
                        "metadata": metadata
                    }])
                    print(f"Upserted chunk: {chunk_id}")
                except Exception as e:
                    print(f"Error during upsert of {chunk_id}: {e}")

        except Exception as e:
            print(f"Error processing Markdown file {md_file_name}: {e}")
