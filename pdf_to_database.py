import os
import numpy as np
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node



from PyPDF2 import PdfReader
import markdownify


new_docs_dir = "new_docs"
os.makedirs(new_docs_dir, exist_ok=True)

#-----------------------------------------Function to convert PDFs to Markdown------------------------------------------

def convert_pdf_to_markdown(pdf_path):
    try:
        # Read the PDF
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Convert the extracted text to Markdown
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


load_dotenv()

OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

pc = Pinecone(api_key=Pinecone_API_Key)

index_name = "cv-markdown-index"
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

#---------------------------------Function to upsert data to index-------------------------------------------

def upsert_markdown_embeddings():
    new_docs_dir = "new_docs"  
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


upsert_markdown_embeddings()


