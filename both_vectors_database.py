import os
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node
from PyPDF2 import PdfReader
import markdownify
import re
from rank_bm25 import BM25Okapi
import numpy as np

load_dotenv()

OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

pc = Pinecone(api_key=Pinecone_API_Key)

data_dir = "data"
new_docs_dir = "new_docs"
os.makedirs(new_docs_dir, exist_ok=True)

# ----------------------------------------- Initialize Pinecone Index -------------------------------------------------

index_name = "cv-analyzer"
namespace = "cvs-info"
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

# -------------------------------------- Function to convert PDFs to Markdown ----------------------------------------

def convert_pdf_to_markdown(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "".join(page.extract_text() for page in reader.pages)
        return markdownify.markdownify(text)
    except Exception as e:
        print(f"Error converting {pdf_path} to Markdown: {e}")
        return None

# --------------------------- Function to check and convert PDFs if not already converted ----------------------------

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

# -------------------------------------------- Check if document exists in Pinecone -----------------------------------

def normalize_doc_id(doc_id):
    """Normalize the document ID to ensure it matches the stored ID in Pinecone."""
    return re.sub(r'\s+', '_', doc_id)

def document_exists_in_pinecone(doc_id, namespace):
    """Check if a document exists in the specified namespace."""
    normalized_doc_id = normalize_doc_id(doc_id)
    try:
        fetch_response = pinecone_index.fetch(ids=[normalized_doc_id], namespace=namespace)
        if fetch_response and 'vectors' in fetch_response and normalized_doc_id in fetch_response['vectors']:
            print(f"Document '{normalized_doc_id}' exists in Pinecone (namespace: {namespace}).")
            return True
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False

# --------------------------------- Function to generate sparse vectors using BM25 ------------------------------------

def generate_bm25_sparse_vector(texts):
    try:
        tokenized_corpus = [text.split() for text in texts]
        bm25 = BM25Okapi(tokenized_corpus)
        sparse_vectors = [bm25.get_scores(doc_tokens) for doc_tokens in tokenized_corpus]
        return sparse_vectors, list(bm25.idf.keys())
    except Exception as e:
        print(f"Error generating BM25 sparse vectors: {e}")
        return None, None

# --------------------------------- Function to generate dense vectors ------------------------------------------------

def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

# --------------------------------- Upsert dense and sparse vectors into Pinecone ------------------------------------

def upsert_markdown_embeddings():
    upserted_docs = []
    all_texts = []

    for filename in os.listdir(new_docs_dir):
        if filename.endswith(".md"):
            markdown_filepath = os.path.join(new_docs_dir, filename)
            with open(markdown_filepath, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read().strip()
                if markdown_content:  # Only add non-empty content
                    all_texts.append(markdown_content)
                else:
                    print(f"Warning: File '{filename}' is empty or invalid.")

    # Generate BM25 sparse vectors-----------------------------------------
    sparse_vectors, feature_names = generate_bm25_sparse_vector(all_texts)
    if sparse_vectors is None or not sparse_vectors:
        print("Failed to generate BM25 sparse vectors. Exiting.")
        return

    print(f"Generated {len(sparse_vectors)} sparse vectors. Feature names: {len(feature_names)}")

    # Upsert both dense and sparse vectors----------------------------------
    for idx, filename in enumerate(os.listdir(new_docs_dir)):
        if filename.endswith(".md"):
            doc_id = os.path.splitext(filename)[0]
            normalized_doc_id = normalize_doc_id(doc_id)

            # Check if the document already exists--------------------------
            if document_exists_in_pinecone(normalized_doc_id, namespace):
                print(f"Document '{normalized_doc_id}' already exists in Pinecone. Skipping upsert.")
                continue
            
            print(f"Document '{doc_id}' does not exist. Adding to Pinecone...")
            # Read markdown content-----------------------------------------
            markdown_filepath = os.path.join(new_docs_dir, filename)
            with open(markdown_filepath, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read()

            # Generate dense embedding--------------------------------------
            dense_embedding = generate_embeddings(markdown_content)

            # Extract sparse vector-----------------------------------------
            bm25_vector = sparse_vectors[idx]
            if bm25_vector.size == 0:  # Check for empty vector
                print(f"Skipping '{normalized_doc_id}': Sparse vector is empty.")
                continue

            # Prepare sparse vector data------------------------------------
            indices = np.nonzero(bm25_vector)[0]  # Non-zero indices
            values = bm25_vector[indices]  # Non-zero values
            sparse_data = {
                "indices": indices.tolist(),
                "values": values.tolist()
            }

            # Prepare metadata
            metadata = {"text": markdown_content}

            try:
                # Upsert with both dense and sparse vectors------------------
                pinecone_index.upsert(
                    vectors=[{
                        "id": normalized_doc_id,
                        "values": dense_embedding,  # Dense vector
                        "metadata": metadata,
                        "sparse_values": {
                            "indices": sparse_data["indices"],
                            "values": sparse_data["values"]
                        }  # Sparse vector
                    }],
                    namespace=namespace
                )
                upserted_docs.append(normalized_doc_id)
                print(f"Upserted vectors: 100%|{'█' * 50}| 1/1 [00:00<00:00]") 
            except Exception as e:
                print(f"Error upserting vectors for document '{normalized_doc_id}': {e}")

    print(f"Upserted {len(upserted_docs)} documents into Pinecone.")

# ----------------------------------------- Main Section -------------------------------------------------------------

if __name__ == "__main__":
    print("Checking and converting PDFs to Markdown if needed...")
    convert_pdfs_to_markdown_if_needed()

    print("Upserting new dense and sparse vectors into Pinecone...")
    upsert_markdown_embeddings()
