import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from pinecone import Pinecone, ServerlessSpec
import io
import os
import openai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
PINECONE_API_KEY = os.getenv("pineconeAPI")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "test-3"
FOLDER_ID = '1whaChKzr1JpKV_O7rxkFQJzaNWy2sPKG'

if not SERVICE_ACCOUNT_FILE or not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
    raise ValueError("Missing required environment variables.")

# Initialize Google Drive API
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive'])
drive_service = build('drive', 'v3', credentials=creds)

# Initialize Pinecone
pinecone_instance = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in [idx.name for idx in pinecone_instance.list_indexes()]:
    pinecone_instance.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=PINECONE_ENVIRONMENT
        )
    )

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "test-3"

# Rest of your code remains unchanged
query = f"'{FOLDER_ID}' in parents and mimeType='text/markdown'"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
files = results.get('files', [])

# Download files and process
if not files:
    logger.info("No markdown files found in the folder.")
else:
    logger.info(f"Found {len(files)} markdown files.")
    markdown_texts = []

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
            markdown_texts.append((file_name, markdown_text))
            logger.info(f"Downloaded: {file_name}")
        except Exception as e:
            logger.error(f"Failed to download file {file_name}: {e}")

    # Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    for file_name, markdown_text in markdown_texts:
        chunks = text_splitter.create_documents([markdown_text])

        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_name}_chunk_{i}"
            try:
                embedding = get_embedding(chunk.page_content)
                index_name.upsert([(chunk_id, embedding, {"text": chunk.page_content})])
                logger.info(f"Upserted chunk {chunk_id} into Pinecone.")
            except Exception as e:
                logger.error(f"Failed to upsert chunk {chunk_id}: {e}")

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']
