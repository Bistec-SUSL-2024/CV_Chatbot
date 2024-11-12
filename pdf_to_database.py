import os
import numpy as np
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.schema import Node



from PyPDF2 import PdfReader
import markdownify

# Create the 'new_docs' directory if it doesn't exist
new_docs_dir = "new_docs"
os.makedirs(new_docs_dir, exist_ok=True)

# Function to convert PDFs to Markdown
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

# Function to check and convert all PDFs in the 'data' directory
def convert_pdfs_in_data_directory():
    pdf_directory = "./data"
    new_files = []

    # Loop through all PDF files in the 'data' directory
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)

            # Create the corresponding markdown file name
            markdown_filename = f"{os.path.splitext(filename)[0]}.md"
            markdown_filepath = os.path.join(new_docs_dir, markdown_filename)

            # Check if the markdown file already exists
            if os.path.exists(markdown_filepath):
                print(f"Markdown file {markdown_filename} already exists. Skipping conversion.")
                continue

            # Convert the PDF to Markdown
            markdown_text = convert_pdf_to_markdown(pdf_path)
            if markdown_text:
                # Save the Markdown content to the file
                with open(markdown_filepath, "w", encoding="utf-8") as md_file:
                    md_file.write(markdown_text)

                new_files.append(markdown_filepath)
                print(f"Converted {filename} to {markdown_filename}.")

    return new_files

# Run the conversion function
new_docs = convert_pdfs_in_data_directory()
print(f"Converted {len(new_docs)} new Markdown documents.")



# Load environment variables
load_dotenv()

# Set OpenAI and Pinecone API keys
OpenAI_Key = os.getenv("OpenAI_Key")
Pinecone_API_Key = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OpenAI_Key
os.environ["PINECONE_API_KEY"] = Pinecone_API_Key

# Initialize Pinecone client
pc = Pinecone(api_key=Pinecone_API_Key)

# Define index name and other settings
index_name = "cv-markdown-index"
namespace = "cv-namespace"
embedding_dimension = 1536  # Assuming the model used gives 1536-dimensional embeddings

# Check if index exists, otherwise create it
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Access the Pinecone index
pinecone_index = pc.Index(index_name)

# Initialize OpenAI embedding model
embed_model = OpenAIEmbedding()

# Function to generate embeddings using OpenAI's API for the markdown text
def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

# Function to check if the document already exists in Pinecone
def document_exists_in_pinecone(doc_id):
    try:
        # Query for the document in Pinecone
        fetch_response = pinecone_index.fetch(ids=[doc_id])
        if 'vectors' in fetch_response and doc_id in fetch_response['vectors']:
            return True  # Document exists in the index
    except Exception as e:
        print(f"Error checking document existence in Pinecone: {e}")
    return False

# Function to process the Markdown files, create embeddings, and upsert them to Pinecone
def upsert_markdown_embeddings():
    new_docs_dir = "new_docs"  # Folder where Markdown files are stored
    existing_docs = os.listdir(new_docs_dir)
    upserted_docs = []

    for filename in existing_docs:
        if filename.endswith(".md"):
            doc_id = os.path.splitext(filename)[0]  # Use filename as document ID (without extension)
            markdown_filepath = os.path.join(new_docs_dir, filename)

            # Check if the document already exists in Pinecone
            if document_exists_in_pinecone(doc_id):
                print(f"Document '{doc_id}' already exists in Pinecone. Skipping upsert.")
                continue

            # Read the Markdown file content
            with open(markdown_filepath, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read()

            # Generate embeddings for the document
            embeddings = generate_embeddings(markdown_content)
            if embeddings:
                # Prepare the record to upsert to Pinecone
                node = Node(id_=doc_id, embedding=embeddings, metadata={"text": markdown_content})
                vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
                vector_store.add(nodes=[node])
                upserted_docs.append(doc_id)
                print(f"Upserted document '{doc_id}' into Pinecone.")

    print(f"Upserted {len(upserted_docs)} new documents into Pinecone.")

# Call the function to upsert Markdown document embeddings into Pinecone
upsert_markdown_embeddings()


#-------------------Ranking part-----------------------------


# def rank_cvs_by_description(job_description):
#     # Generate the embedding for the job description
#     query_embedding = generate_embeddings(job_description)
    
#     if query_embedding is None:
#         print("Error: Failed to generate embedding for the job description.")
#         return []
    
#     # Query Pinecone to find the most similar CVs
#     query_results = pinecone_index.query(
#         vector=query_embedding,
#         top_k=5,  # Get top 5 closest matches (can adjust based on need)
#         include_metadata=True,
#         namespace=namespace
#     )
    
#     # Process the query results (sorted by score)
#     ranked_cvs = []
#     for match in query_results['matches']:
#         cv_id = match['id']
#         score = match['score']
#         metadata = match['metadata']
#         ranked_cvs.append({
#             "cv_id": cv_id,
#             "score": score,
#             "metadata": metadata
#         })
    
#     # Sort by score (most similar CVs first)
#     ranked_cvs.sort(key=lambda x: x['score'], reverse=True)
    
#     return ranked_cvs

# # Example usage
# job_description = "We are looking for a project manager with experience in leading teams and managing deadlines."

# # Rank CVs based on the job description
# ranked_cvs = rank_cvs_by_description(job_description)

# # Print the ranked CVs
# if ranked_cvs:
#     print("Top ranked CVs based on job description:")
#     for idx, cv in enumerate(ranked_cvs, 1):
#         print(f"{idx}. CV ID: {cv['cv_id']}, Similarity Score: {cv['score']:.4f}")
#         print(f"   CV Text Excerpt: {cv['metadata']['text'][:300]}...")  # Display a snippet of the CV text
# else:
#     print("No CVs found for ranking.")