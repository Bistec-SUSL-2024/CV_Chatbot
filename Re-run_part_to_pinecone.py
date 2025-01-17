import os
import io
import re
import time
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdownify
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node

# ------------------------------------Load Environment Variables------------------------------------------------------------------

load_dotenv()

SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")
OpenAI_Key = os.getenv("Open_ai_key")
Pinecone_API_Key = os.getenv("PINECONE_API")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

# --------------------------------------Initialize Google Drive API Service--------------------------------------------------------

def initialize_service():
    if not SERVICE_ACCOUNT_PATH:
        raise ValueError("SERVICE_ACCOUNT_PATH is not set in the .env file")
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
    return build('drive', 'v3', credentials=creds)

# --------------------------------------Initialize Pinecone API---------------------------------------------------------------------

pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "test"
embedding_dimension = 1536

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
pinecone_index = pc.Index(index_name)
embed_model = OpenAIEmbedding()

# --------------------------------------Utility Functions--------------------------------------------------------------------------

def normalize_doc_id(doc_id):
    return re.sub(r'\s+', '_', doc_id)

def document_exists_in_pinecone(doc_id):
    normalized_doc_id = normalize_doc_id(doc_id)
    try:
        fetch_response = pinecone_index.fetch(ids=[normalized_doc_id])
        if fetch_response and 'vectors' in fetch_response and normalized_doc_id in fetch_response['vectors']:
            return True
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False

def generate_embeddings(text):
    try:
        return embed_model.get_text_embedding(text)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

def convert_pdf_to_markdown(pdf_content):
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        return markdownify.markdownify(text)
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return None

def upload_markdown_to_drive(markdown_content, filename, folder_id, drive_service):
    try:
        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            'mimeType': 'text/markdown'
        }
        media = MediaIoBaseUpload(io.BytesIO(markdown_content.encode("utf-8")), mimetype='text/markdown')
        drive_service.files().create(body=file_metadata, media_body=media).execute()
        print(f"Successfully uploaded {filename} to Google Drive folder.")
    except Exception as e:
        print(f"Error uploading {filename} to Google Drive: {e}")

# --------------------------------------Processing Functionality-------------------------------------------------------------------

def process_new_file(file_id, file_name, drive_service, target_folder_id):
    try:
        # ----------------------------------------------------Download the PDF-----------------------------

        request = drive_service.files().get_media(fileId=file_id)
        pdf_content = request.execute()

        if not pdf_content:
            print(f"Failed to download {file_name}.")
            return

        #---------------------------------------------------------- Convert to Markdown--------------------------------------------

        markdown_content = convert_pdf_to_markdown(pdf_content)
        if not markdown_content:
            print(f"Failed to convert {file_name} to Markdown.")
            return

        # ---------------------------------Upload Markdown to Drive---------------------------------------------------------------------------

        markdown_filename = f"{os.path.splitext(file_name)[0]}.md"
        upload_markdown_to_drive(markdown_content, markdown_filename, target_folder_id, drive_service)

        # -------------------------------Generate and upsert embeddings into Pinecone-------------------------------------------------------------

        doc_id = os.path.splitext(file_name)[0]
        normalized_doc_id = normalize_doc_id(doc_id)

        if document_exists_in_pinecone(normalized_doc_id):
            print(f"Document '{normalized_doc_id}' already exists in Pinecone. Skipping upsert.")
            return

        embeddings = generate_embeddings(markdown_content)
        if embeddings:
            node = Node(id_=normalized_doc_id, embedding=embeddings, metadata={"text": markdown_content})
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            vector_store.add(nodes=[node])
            print(f"Upserted document '{normalized_doc_id}' into Pinecone.")
    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

def fetch_files(service, folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    response = service.files().list(q=query).execute()
    return {file['id']: file['name'] for file in response.get('files', [])}

# --------------------------------------Monitor Folder for Changes-----------------------------------------------------------------

def monitor_folder(source_folder_id, target_folder_id):
    drive_service = initialize_service()
    previous_files = fetch_files(drive_service, source_folder_id)
    print("Monitoring folder...")

    while True:
        time.sleep(10)  # Check every 10 seconds
        current_files = fetch_files(drive_service, source_folder_id)
        if len(current_files) > len(previous_files):
            new_files = set(current_files.keys()) - set(previous_files.keys())
            for file_id in new_files:
                print(f"New file detected: {current_files[file_id]}")
                process_new_file(file_id, current_files[file_id], drive_service, target_folder_id)
            previous_files = current_files

# --------------------------------------Main--------------------------------------------------------------------------------------

if __name__ == "__main__":
    SOURCE_FOLDER_ID = '1tS1F0CoeaQy3NWBaWaU8foCoStmfZ0Fv'  # CV_Storage
    TARGET_FOLDER_ID = '1AYZuzhd9qa1gZXARx2-9zEk79runGvve'  # Markdown_Cvs
    monitor_folder(SOURCE_FOLDER_ID, TARGET_FOLDER_ID)
