import os
import io
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
import pinecone
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Google Drive API setup
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=creds)

# OpenAI API setup
OPENAI_API_KEY = os.getenv("openaiKEY")
openai.api_key = OPENAI_API_KEY

# Pinecone setup
PINECONE_API_KEY = os.getenv("pineconeAPI")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PineconeIndex")

# Initialize Pinecone instance
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Check and create the index if necessary
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,  # Embedding dimension
        metric="cosine",
        spec=ServerlessSpec(cloud='aws', region='us-west-2')  # Adjust based on your cloud provider and region
    )

index = pc.Index(INDEX_NAME)

# Function to generate embeddings using OpenAI
def generate_embedding(text):
    try:
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Function to split text into chunks
def chunk_text(text, chunk_size=750, overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    return text_splitter.create_documents([text])

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

            # Chunk the text
            chunks = chunk_text(markdown_text)

            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_name}_chunk_{i}"
                embedding = generate_embedding(chunk.page_content)

                if embedding:
                    metadata = {"text": chunk.page_content}

                    # Upsert the embedding into Pinecone
                    try:
                        index.upsert(vectors=[{
                            "id": chunk_id,
                            "values": embedding,
                            "metadata": metadata
                        }])
                        print(f"Upserted chunk: {chunk_id}")
                    except Exception as e:
                        print(f"Error during upsert of {chunk_id}: {e}")
                else:
                    print(f"Skipping chunk {i} due to embedding generation error.")

        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
