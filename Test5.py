import os
import shutil
import pdfplumber
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    load_index_from_storage,
)


load_dotenv()
OpenAI_Key = os.getenv("Open_ai_key")
os.environ["OPENAI_API_KEY"] = OpenAI_Key


PERSIST_DIR = "./storage"
index = None

def clear_storage():
    """Clear the storage directory to reset the index."""
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
        print("Cleared existing index storage.")

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return text

def rebuild_index():
    global index
    
   
    clear_storage()
    
    
    cv_files = os.listdir("data")[:5]
    
    if not cv_files:
        print("Data directory is empty. Index will not be created.")
        return  

    documents = []
    for file in cv_files:
        file_path = os.path.join("data", file)
        
        # Ensure we only attempt to read files (not directories)
        if os.path.isfile(file_path):
            print(f"Loading CV from: {file_path}")
            
            # Extract content based on file type
            if file.lower().endswith(".pdf"):
                content = extract_text_from_pdf(file_path)
            else:
                # For other text-based files (e.g., .txt)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
          
            if content.strip():
                document = Document(content=content)
                documents.append(document)
            else:
                print(f"Skipped empty document: {file_path}")

   
    print(f"Loaded {len(documents)} documents for indexing.")

    if documents:
        
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("Index has been created and stored.")
    else:
        print("No valid documents found to index.")

def query_cv(prompt):
    global index
    
    # Check if index has been loaded or created
    if index is None:
        raise ValueError("Index has not been initialized. Please check the data directory or persisted storage.")

  
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    
    
    return str(response) if response else "No relevant information found in the documents."


rebuild_index()  


result = query_cv("I have a job description that requires Python and Django skills. Who among these candidates has these skills?")
print(result)
