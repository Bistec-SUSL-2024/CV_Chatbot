import os
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import markdownify
import re

load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

#-----------------------------------------Initialize Pinecone and set namespace--------------------------------------

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "cv-analyzer"
namespace = "dense_vectors"
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

data_dir = "data"
new_docs_dir = "new_docs"
os.makedirs(new_docs_dir, exist_ok=True)

#-----------------------------------------Function to convert PDFs to Markdown------------------------------------------

def convert_pdf_to_markdown(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() for page in reader.pages)
        return markdownify.markdownify(text)
    except Exception as e:
        print(f"Error converting {pdf_path} to Markdown: {e}")
        return None

#-----------------------------------------------------Check if document exists in Pinecone-------------------------------

def check_existence_in_pinecone(ids, namespace):
    try:
        fetch_response = pinecone_index.fetch(ids=ids, namespace=namespace)
        return fetch_response.get("vectors", {})
    except Exception as e:
        print(f"Error checking existence in Pinecone: {e}")
        return {}

#-----------------------------------Store Markdown files in Pinecone with existence check---------------------------------

def store_markdown_embeddings_with_check():
    for filename in os.listdir(new_docs_dir):
        if filename.endswith(".md"):
            doc_id = re.sub(r'\s+', '_', os.path.splitext(filename)[0])  # Normalize document ID
            markdown_filepath = os.path.join(new_docs_dir, filename)
            existing_vectors = check_existence_in_pinecone([doc_id], namespace)

            if doc_id not in existing_vectors:
                print(f"Document '{doc_id}' does not exist. Adding to Pinecone...")
                with open(markdown_filepath, "r", encoding="utf-8") as md_file:
                    markdown_content = md_file.read()
                
                embedding = embed_model.get_text_embedding(markdown_content)
                
                
                upsert_response = pinecone_index.upsert([{
                    "id": doc_id,
                    "values": embedding,
                    "metadata": {"content": markdown_content}
                }], namespace=namespace)
                
                print(f"Upserted vectors: 100%|{'█' * 50}| 1/1 [00:00<00:00]")  
            else:
                print(f"Document '{doc_id}' already exists in Pinecone. Skipping upsert.")

#------------------------------Main function to process PDFs and store embeddings--------------------------------------

def upsert_process_and_store_pdfs():
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(data_dir, filename)
            markdown_filename = f"{os.path.splitext(filename)[0]}.md"
            markdown_filepath = os.path.join(new_docs_dir, markdown_filename)

            if not os.path.exists(markdown_filepath):
                markdown_text = convert_pdf_to_markdown(pdf_path)
                if markdown_text:
                    with open(markdown_filepath, "w", encoding="utf-8") as md_file:
                        md_file.write(markdown_text)
                    print(f"Converted '{filename}' to Markdown.")
            else:
                print(f"Markdown file '{markdown_filename}' already exists. Skipping conversion.")

    print("Upserting new Markdown documents into Pinecone...")
    store_markdown_embeddings_with_check()

#----------------------------------------Main Function-------------------------------------------------

if __name__ == "__main__":

    print("Checking and converting PDFs to Markdown if needed...")
    upsert_process_and_store_pdfs()
