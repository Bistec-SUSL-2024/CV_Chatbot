import os
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node
from PyPDF2 import PdfReader
import markdownify
import re


load_dotenv()

OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

pc = Pinecone(api_key=Pinecone_API_Key)


data_dir = "data"
new_docs_dir = "new_docs"
os.makedirs(new_docs_dir, exist_ok=True)

#--------------------------------------Function to convert PDFs to Markdown----------------------------------------

def convert_pdf_to_markdown(pdf_path):
    try:
        
        reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() for page in reader.pages)

        markdown_text = markdownify.markdownify(text)
        return markdown_text
    except Exception as e:
        print(f"Error converting {pdf_path} to Markdown: {e}")
        return None

#--------------------------------Function to check and convert PDFs if not already converted-------------------------

def convert_pdfs_to_markdown_if_needed():
    converted_files = []

    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(data_dir, filename)
            markdown_filename = f"{os.path.splitext(filename)[0]}.md"
            markdown_filepath = os.path.join(new_docs_dir, markdown_filename)

            if os.path.exists(markdown_filepath):
                print(f"Markdown file '{markdown_filename}' already exists. Skipping conversion.")
                continue

            markdown_text = convert_pdf_to_markdown(pdf_path)
            if markdown_text:
                with open(markdown_filepath, "w", encoding="utf-8") as md_file:
                    md_file.write(markdown_text)

                converted_files.append(markdown_filepath)
                print(f"Converted '{filename}' to Markdown.")
    return converted_files

#--------------------------------------------Check if document exists in Pinecone--------------------------------------

def normalize_doc_id(doc_id):
    """Normalize the document ID to ensure it matches the stored ID in Pinecone."""
    normalized_id = re.sub(r'\s+', '_', doc_id)  
    return normalized_id

def document_exists_in_pinecone(doc_id):
    normalized_doc_id = normalize_doc_id(doc_id)  
    try:
        fetch_response = pinecone_index.fetch(ids=[normalized_doc_id])
        
        if fetch_response and 'vectors' in fetch_response and normalized_doc_id in fetch_response['vectors']:
            print(f"Document '{normalized_doc_id}' exists in Pinecone.")
            return True
        else:
            print(f"Document '{normalized_doc_id}' does not exist in Pinecone.")
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False

#--------------------------------Upsert embeddings into Pinecone if not already upserted-----------------------------

def upsert_markdown_embeddings():
    upserted_docs = []

    for filename in os.listdir(new_docs_dir):
        if filename.endswith(".md"):
            doc_id = os.path.splitext(filename)[0]  # Get document ID (filename without extension)
            normalized_doc_id = normalize_doc_id(doc_id)  

            markdown_filepath = os.path.join(new_docs_dir, filename)

            
            if document_exists_in_pinecone(normalized_doc_id):
                print(f"Document '{normalized_doc_id}' already exists in Pinecone. Skipping upsert.")
                continue

            with open(markdown_filepath, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read()

            embeddings = generate_embeddings(markdown_content)
            if embeddings:
                node = Node(id_=normalized_doc_id, embedding=embeddings, metadata={"text": markdown_content})
                vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
                vector_store.add(nodes=[node])
                upserted_docs.append(normalized_doc_id)
                print(f"Upserted document '{normalized_doc_id}' into Pinecone.")
    print(f"Upserted {len(upserted_docs)} new documents into Pinecone.")


#-----------------------------------------Load environment and initialize Pinecone--------------------------------------

index_name = "cv-markdown-index-3"
namespace = ""
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

#-----------------------------------------Function to generate text embeddings----------------------------------------

def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

#------------------------------------------------Main Section--------------------------------------------------------

if __name__ == "__main__":
    print("Checking and converting PDFs to Markdown if needed...")
    convert_pdfs_to_markdown_if_needed()

    print("Upserting new Markdown documents into Pinecone...")
    upsert_markdown_embeddings()
