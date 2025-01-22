import os
import io
import re
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdownify
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

#------------------------------------------------ Load environment variables---------------------------------------------------------------------------------

load_dotenv()

OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")
SERVICE_ACCOUNT_FILE = os.getenv("Service_AP")      #------add the path to the service account file--------------------------------------------

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "test-tt"
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

SOURCE_FOLDER_ID = os.getenv("CV_storage")  # CV_Storage
TARGET_FOLDER_ID = os.getenv("Md_CV_Storage")  # Markdown_Cvs


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

#----------------------------------------------------Genarate_Embeddings-------------------------------------------------------------------------

def generate_embeddings(text):
    """Generate embeddings for the provided text."""
    try:
        return embed_model.get_text_embedding(text)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

#-----------------------------------------------------Convert_PDF_to_Markdown-----------------------------------------------------------------------

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

#-----------------------------------------------------File_Existence_in_Drive-----------------------------------------------------------------------

def upload_markdown_to_drive(markdown_content, filename, folder_id):
    """Upload Markdown file to Google Drive if it doesn't already exist in the folder."""
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


def process_pdfs_from_drive():
    """Fetch, process, and store PDFs from Google Drive with pagination."""
    page_token = None  # Initialize page token for pagination

    while True:
        # ----------------------------Fetch files from Google Drive-------------------------------------------------------------------------------
        
        results = drive_service.files().list(
            q=f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/pdf'",
            pageSize=100,  # Fetch up to 100 files per API call
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
                # --------------------------------------------------Download the PDF----------------------------------------------------------------

                request = drive_service.files().get_media(fileId=file_id)
                pdf_content = request.execute()

                if not pdf_content:
                    print(f"Failed to download {file_name}.")
                    continue

                #---------------------------------------------------- Convert to Markdown-----------------------------------------------------------------

                markdown_content = convert_pdf_to_markdown(pdf_content)
                if not markdown_content:
                    print(f"Failed to convert {file_name} to Markdown.")
                    continue

                #----------------------------------------------------- Upload Markdown to Drive------------------------------------------------------------

                markdown_filename = f"{os.path.splitext(file_name)[0]}.md"
                upload_markdown_to_drive(markdown_content, markdown_filename, TARGET_FOLDER_ID)

                # -----------------------------------------------------Generate and upsert embeddings into Pinecone-----------------------------------------------

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
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

        # ---------------------------------------------------Update page token to fetch the next page-----------------------------------------------

        page_token = results.get('nextPageToken')
        if not page_token:
            break  # No more pages, exit the loop

#--------------------------------------------------------Main_Section---------------------------------------------------------------------------------

if __name__ == "__main__":
    print("Processing PDFs from Google Drive...")
    process_pdfs_from_drive()
