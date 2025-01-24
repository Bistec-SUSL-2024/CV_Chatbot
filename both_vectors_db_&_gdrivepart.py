import os
import io
import re
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdownify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node
from rank_bm25 import BM25Okapi
import numpy as np

#------------------------------------------------ Load environment variables ---------------------------------------------- 

load_dotenv()

OpenAI_Key = os.getenv("Open_ai_key")
Pinecone_API_Key = os.getenv("PINECONE_API")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_PATH1")  # Add the path to the service account file

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

pc = Pinecone(api_key=Pinecone_API_Key)
index_name = "test-3"
namespace = "cvs-info"
embedding_dimension = 1536

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        metric="dotproduct",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
pinecone_index = pc.Index(index_name)
embed_model = OpenAIEmbedding()

SOURCE_FOLDER_ID = ""  # Change this to your source folder ID
TARGET_FOLDER_ID = ""  # Change this to your target folder ID

# ---------------------------- Normalize document ID ----------------------------

def normalize_doc_id(doc_id):
    """Normalize the document ID to ensure it matches the stored ID in Pinecone."""
    return re.sub(r'\s+', '_', doc_id)

# ---------------------------- Check if document exists in Pinecone ----------------------------

def document_exists_in_pinecone(doc_id, namespace):
    """Check if a document exists in the specified namespace."""
    normalized_doc_id = normalize_doc_id(doc_id)
    try:
        fetch_response = pinecone_index.fetch(ids=[normalized_doc_id], namespace=namespace)
        if fetch_response and 'vectors' in fetch_response and normalized_doc_id in fetch_response['vectors']:
            print(f"Document '{normalized_doc_id}' exists in Pinecone.")
            return True
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False

# ---------------------------- Convert PDF to Markdown ----------------------------

def convert_pdf_to_markdown(pdf_content):
    """Convert PDF content to Markdown format."""
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        return markdownify.markdownify(text)
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return None

# ---------------------------- Generate Embeddings ----------------------------

def generate_embeddings(text):
    """Generate embeddings for the provided text."""
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

# ---------------------------- Generate Sparse Vectors (BM25) ----------------------------


def generate_bm25_sparse_vector(texts):
    try:
        tokenized_corpus = [text.split() for text in texts]
        bm25 = BM25Okapi(tokenized_corpus)
        sparse_vectors = [bm25.get_scores(doc_tokens) for doc_tokens in tokenized_corpus]
        return sparse_vectors
    except Exception as e:
        print(f"Error generating BM25 sparse vectors: {e}")
        return None

# ---------------------------- Upload Markdown to Google Drive ----------------------------


def upload_markdown_to_drive(markdown_content, filename, folder_id):
    """Upload Markdown file to Google Drive if it doesn't already exist in the folder."""
    try:
        # Check if the file already exists in the target folder
        existing_files = drive_service.files().list(
            q=f"'{folder_id}' in parents and name='{filename}'",
            fields="files(id, name)"
        ).execute()

        if existing_files.get('files'):
            print(f"File '{filename}' already exists in the folder. Skipping upload.")
            return  # Skip upload if file exists

        # If file doesn't exist, upload the new file
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

# ---------------------------- Process PDFs from Google Drive ----------------------------


def process_pdfs_from_drive():
    """Fetch, process, and store PDFs from Google Drive with pagination."""
    page_token = None  # Initialize page token for pagination

    while True:
        # ---------------------------- Fetch files from Google Drive ----------------------------

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
                # ---------------------------- Download the PDF ----------------------------

                request = drive_service.files().get_media(fileId=file_id)
                pdf_content = request.execute()

                if not pdf_content:
                    print(f"Failed to download {file_name}.")
                    continue

                # ---------------------------- Convert to Markdown ----------------------------

                markdown_content = convert_pdf_to_markdown(pdf_content)
                if not markdown_content:
                    print(f"Failed to convert {file_name} to Markdown.")
                    continue

                # ---------------------------- Upload Markdown to Drive ----------------------------

                markdown_filename = f"{os.path.splitext(file_name)[0]}.md"
                upload_markdown_to_drive(markdown_content, markdown_filename, TARGET_FOLDER_ID)

                # ---------------------------- Generate and upsert embeddings into Pinecone ----------------------------

                doc_id = os.path.splitext(file_name)[0]
                normalized_doc_id = normalize_doc_id(doc_id)

                if document_exists_in_pinecone(normalized_doc_id, namespace):
                    print(f"Document '{normalized_doc_id}' already exists in Pinecone. Skipping upsert.")
                    continue

                # Generate dense and sparse vectors

                dense_embedding = generate_embeddings(markdown_content)
                sparse_vectors = generate_bm25_sparse_vector([markdown_content])

                if dense_embedding and sparse_vectors:
                    # Prepare sparse vector data for upsert

                    sparse_vector = sparse_vectors[0]  # Get the sparse vector for the current document
                    indices = np.nonzero(sparse_vector)[0]  # Non-zero indices
                    values = sparse_vector[indices]  # Non-zero values
                    sparse_data = {
                        "indices": indices.tolist(),
                        "values": values.tolist()
                    }

                    # Upsert the data into Pinecone with both dense and sparse vectors

                    try:
                        pinecone_index.upsert(
                            vectors=[{
                                "id": normalized_doc_id,
                                "values": dense_embedding,  # Dense vector
                                "metadata": {"text": markdown_content},
                                "sparse_values": sparse_data  # Sparse vector data
                            }],
                            namespace=namespace
                        )
                        print(f"Upserted document '{normalized_doc_id}' into Pinecone with both dense and sparse vectors.")
                    except Exception as e:
                        print(f"Error upserting vectors for document '{normalized_doc_id}': {e}")
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

        # ---------------------------- Update page token to fetch the next page ----------------------------

        page_token = results.get('nextPageToken')
        if not page_token:
            break  # No more pages, exit the loop

# ---------------------------- Main Section ----------------------------

if __name__ == "__main__":
    print("Processing PDFs from Google Drive...")
    process_pdfs_from_drive()
