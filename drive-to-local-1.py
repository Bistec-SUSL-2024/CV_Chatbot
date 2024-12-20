import os
import io
import re
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdownify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node

# Load environment variables
load_dotenv()

OpenAI_Key = os.getenv("Open_ai_key")
Pinecone_API_Key = os.getenv("PINECONE_API")
SERVICE_ACCOUNT_FILE = " "       #-----------Add the path to the service account file-------------------------------------------------------

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

#------------------------------------------------ Google Drive API Setup---------------------------------------------------------------------------------
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

#------------------------------------------------- Pinecone Setup-----------------------------------------------------------------------------------------
pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "test-3"
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


SOURCE_FOLDER_ID = '1pd3FKMd-3Vm7hESaerxAyGzoOJa7LxZX'  # CV_Storage
LOCAL_MARKDOWN_FOLDER = "./local_markdown_storage"  # Local folder to store Markdown files

# Ensure the local Markdown folder exists
if not os.path.exists(LOCAL_MARKDOWN_FOLDER):
    os.makedirs(LOCAL_MARKDOWN_FOLDER)


def normalize_doc_id(doc_id):
    """Normalize document IDs to be Pinecone-friendly."""
    return re.sub(r'\s+', '_', doc_id)


def document_exists_in_pinecone(doc_id):
    """Check if a document already exists in Pinecone."""
    normalized_doc_id = normalize_doc_id(doc_id)
    try:
        fetch_response = pinecone_index.fetch(ids=[normalized_doc_id])
        if fetch_response and 'vectors' in fetch_response and normalized_doc_id in fetch_response['vectors']:
            return True
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False


def generate_embeddings(text):
    """Generate embeddings for the provided text."""
    try:
        return embed_model.get_text_embedding(text)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None


def convert_pdf_to_markdown(pdf_content):
    """Convert PDF content to Markdown format."""
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        markdown_text = markdownify.markdownify(text)
        return markdown_text
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return None


def process_pdfs_from_drive():
    """Fetch, process, and store PDFs from Google Drive."""
    page_token = None  # Initialize page token for pagination
    processed_files_count = 0  # Track the number of processed files

    while True:
        # Fetch files from Google Drive
        results = drive_service.files().list(
            q=f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/pdf'",
            pageSize=100,  # Increase the page size to fetch more files per request
            fields="nextPageToken, files(id, name)",  # Include nextPageToken for pagination
            pageToken=page_token  # Use the page token to get the next set of files
        ).execute()

        files = results.get('files', [])
        if not files:
            print("No more PDF files found in the specified folder.")
            break

        for file in files:
            file_id = file['id']
            file_name = file['name']
            print(f"Processing file: {file_name} (ID: {file_id})")

            try:
                # Download the PDF
                request = drive_service.files().get_media(fileId=file_id)
                pdf_content = request.execute()

                if not pdf_content:
                    print(f"Failed to download {file_name}.")
                    continue

                # Convert to Markdown
                markdown_content = convert_pdf_to_markdown(pdf_content)
                if not markdown_content:
                    print(f"Failed to convert {file_name} to Markdown.")
                    continue

                # Save Markdown locally
                markdown_filename = f"{os.path.splitext(file_name)[0]}.md"
                markdown_file_path = os.path.join(LOCAL_MARKDOWN_FOLDER, markdown_filename)
                with open(markdown_file_path, "w", encoding="utf-8") as md_file:
                    md_file.write(markdown_content)
                print(f"Saved Markdown file locally: {markdown_file_path}")

                # Generate and upsert embeddings into Pinecone
                doc_id = os.path.splitext(file_name)[0]
                normalized_doc_id = normalize_doc_id(doc_id)

                if document_exists_in_pinecone(normalized_doc_id):
                    print(f"Document '{normalized_doc_id}' already exists in Pinecone. Skipping upsert.")
                    continue

                embeddings = generate_embeddings(markdown_content)
                if embeddings:
                    node = Node(id_=normalized_doc_id, embedding=embeddings, metadata={"text": markdown_content})
                    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
                    vector_store.add(nodes=[node])
                    print(f"Upserted document '{normalized_doc_id}' into Pinecone.")
                    processed_files_count += 1
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

        
        page_token = results.get('nextPageToken')
        if not page_token:
            break  

    print(f"Processing complete. Total files processed: {processed_files_count}")


if __name__ == "__main__":
    print("Processing PDFs from Google Drive, saving Markdown locally, and upserting into Pinecone...")
    process_pdfs_from_drive()
