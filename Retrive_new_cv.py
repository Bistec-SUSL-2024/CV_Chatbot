import os
import numpy as np
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node
from PyPDF2 import PdfReader
import markdownify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload

# Load environment variables
load_dotenv()
OpenAI_Key = os.getenv("Open_ai_key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "cv-markdown-index"
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

def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

def document_exists_in_pinecone(doc_id):
    try:
        fetch_response = pinecone_index.fetch(ids=[doc_id])
        return 'vectors' in fetch_response and doc_id in fetch_response['vectors']
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False

def upsert_markdown_embeddings(doc_id, markdown_content):
    if document_exists_in_pinecone(doc_id):
        print(f"Document '{doc_id}' already exists in Pinecone. Skipping upsert.")
        return

    embeddings = generate_embeddings(markdown_content)
    if embeddings:
        node = Node(id_=doc_id, embedding=embeddings, metadata={"text": markdown_content})
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        vector_store.add(nodes=[node])
        print(f"Upserted document '{doc_id}' into Pinecone.")

def convert_pdf_to_markdown(pdf_content):
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        markdown_text = markdownify.markdownify(text)
        return markdown_text
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return None

def list_drive_files():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-file.json'  # Update this path

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)

    folder_id = 'your_folder_id_here'
    
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/pdf'",
        pageSize=10,
        fields="nextPageToken, files(id, name)"
    ).execute()
    
    return results.get('files', [])

def download_and_upsert_drive_files(files):
    service = build('drive', 'v3', credentials=service_account.Credentials.from_service_account_file('path/to/your/service-account-file.json'))
    
    for file in files:
        file_id = file['id']
        
        request = service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        
        pdf_content = fh.getvalue()
        
        # Convert PDF content to Markdown and upsert to Pinecone
        markdown_content = convert_pdf_to_markdown(pdf_content)
        
        if markdown_content:
            doc_id = file['name'].replace('.pdf', '')  # Use the file name as the document ID
            upsert_markdown_embeddings(doc_id, markdown_content)

# Main execution flow
if __name__ == "__main__":
    drive_files = list_drive_files()
    
    if drive_files:
        download_and_upsert_drive_files(drive_files)