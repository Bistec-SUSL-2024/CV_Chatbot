import os
import numpy as np
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
from astrapy import DataAPIClient
from astrapy.constants import VectorMetric
from astrapy.database import Database

from PyPDF2 import PdfReader
import markdownify

load_dotenv()

new_docs_dir = "new_docs"
os.makedirs(new_docs_dir, exist_ok=True)

# Load environment variables
astra_db_api_endpoint = os.getenv("ASTRA_DB_ENDPOINT_URL")
astra_db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
openai_key = os.getenv("Open_ai_key")

os.environ["OPENAI_API_KEY"] = openai_key

# Initialize Astra DB client
client = DataAPIClient(astra_db_application_token)
database = client.get_database(astra_db_api_endpoint)

# Create or get an existing collection with appropriate dimensions for embeddings
collection = database.create_collection(
    "cv_markdown_collection",  
    dimension=1536,
    metric=VectorMetric.COSINE,  
    keyspace="default_keyspace",  # Ensure this matches your existing keyspace name in AstraDB
    check_exists=False, # Optional.
)

embed_model = OpenAIEmbedding()

#-----------------------------------------Function to convert PDFs to Markdown------------------------------------------
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

#----------------------------------Function to check and convert all PDFs in the 'data' directory-------------------------------
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

new_docs = convert_pdfs_in_data_directory()
print(f"Converted {len(new_docs)} new Markdown documents.")

#-----------------------------------------Generate Embeddings Function-----------------------------------------
def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

#---------------------------------Function to check if document exists in Astra DB-------------------------------------------
def document_exists_in_astra(doc_id):
    try:
        response = collection.find({"id": doc_id})
        return len(response) > 0
    except Exception as e:
        print(f"Error checking document existence in Astra DB: {e}")
    return False

#---------------------------------Function to upsert data to Astra DB-------------------------------------------
def upsert_markdown_embeddings():
    new_docs_dir = "new_docs"
    existing_docs = os.listdir(new_docs_dir)
    upserted_docs = []

    for filename in existing_docs:
        if filename.endswith(".md"):
            doc_id = os.path.splitext(filename)[0]
            markdown_filepath = os.path.join(new_docs_dir, filename)
            if document_exists_in_astra(doc_id):
                print(f"Document '{doc_id}' already exists in Astra DB. Skipping upsert.")
                continue
            with open(markdown_filepath, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read()
            embeddings = generate_embeddings(markdown_content)
            if embeddings:
                document = {
                    "id": doc_id,
                    "text": markdown_content,
                    "$vector": embeddings
                }
                collection.insert_one(document)
                upserted_docs.append(doc_id)
                print(f"Upserted document '{doc_id}' into Astra DB.")
    print(f"Upserted {len(upserted_docs)} new documents into Astra DB.")

upsert_markdown_embeddings()
