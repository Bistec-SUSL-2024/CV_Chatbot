import os
import numpy as np
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node
from PyPDF2 import PdfReader
import markdownify

# Google Drive API imports
from google.oauth2 import service_account
from googleapiclient.discovery import build

new_docs_dir = "new_docs"
os.makedirs(new_docs_dir, exist_ok=True)

# Function to convert PDFs to Markdown
def convert_pdf_to_markdown(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        markdown_text = markdownify.markdownify(text)
        return markdown_text
    except Exception as e:
        print(f"Error converting {pdf_path} to Markdown: {e}")
        return None

# Function to check and convert all PDFs in the 'data' directory
def convert_pdfs_in_data_directory():
    pdf_directory = "./data"
    new_files = []
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            markdown_filename = f"{os.path.splitext(filename)[0]}.md"
            markdown_filepath = os.path.join(new_docs_dir, markdown_filename)

            if os.path.exists(markdown_filepath):
                print(f"Markdown file {markdown_filename} already exists. Skipping conversion.")
                continue

            markdown_text = convert_pdf_to_markdown(pdf_path)
            if markdown_text:
                with open(markdown_filepath, "w", encoding="utf-8") as md_file:
                    md_file.write(markdown_text)
                new_files.append(markdown_filepath)
                print(f"Converted {filename} to {markdown_filename}.")
    return new_files

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
        if 'vectors' in fetch_response and doc_id in fetch_response['vectors']:
            return True  
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False

# Function to upsert data to index
def upsert_markdown_embeddings():
    existing_docs = os.listdir(new_docs_dir)
    upserted_docs = []
    
    for filename in existing_docs:
        if filename.endswith(".md"):
            doc_id = os.path.splitext(filename)[0]  
            markdown_filepath = os.path.join(new_docs_dir, filename)

            if document_exists_in_pinecone(doc_id):
                print(f"Document '{doc_id}' already exists in Pinecone. Skipping upsert.")
                continue

            with open(markdown_filepath, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read()

            embeddings = generate_embeddings(markdown_content)
            if embeddings:
                node = Node(id_=doc_id, embedding=embeddings, metadata={"text": markdown_content})
                vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
                vector_store.add(nodes=[node])
                upserted_docs.append(doc_id)
                print(f"Upserted document '{doc_id}' into Pinecone.")

    print(f"Upserted {len(upserted_docs)} new documents into Pinecone.")

# Function to authenticate and list files from Google Drive
def list_drive_files():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    SERVICE_ACCOUNT_FILE = 'path/to/your/service-account-file.json'  # Update this path

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)

    # Replace 'CV_Storage' with your actual folder name or ID.
    folder_id = 'your_folder_id_here'
    
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/pdf'",
        pageSize=10,
        fields="nextPageToken, files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    
    return items

# Function to download files from Google Drive
def download_drive_files(files):
    for file in files:
        file_id = file['id']
        file_name = file['name']
        
        request = service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        
        # Save the PDF locally
        pdf_path = os.path.join("./data", file_name)
        
        with open(pdf_path, 'wb') as f:
            f.write(fh.getbuffer())
        
        print(f"Downloaded {file_name} from Google Drive.")

# Main execution flow
if __name__ == "__main__":
    # Convert local PDFs if any exist
    new_docs_from_local_pdfs = convert_pdfs_in_data_directory()
    
    # List and download CVs from Google Drive
    drive_files = list_drive_files()
    
    if drive_files:
        download_drive_files(drive_files)
    
    # Convert downloaded PDFs from Google Drive to Markdown format
    convert_pdfs_in_data_directory()  # Re-use this function for newly downloaded files
    
    # Upsert all Markdown embeddings into Pinecone
    upsert_markdown_embeddings()