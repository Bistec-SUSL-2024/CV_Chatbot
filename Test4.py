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
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    print(f"Warning: No text found on page {page_num + 1} of {file_path}")
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
    owner_names = []  # Keep track of each CV owner's name
    for file in cv_files:
        file_path = os.path.join("data", file)
        
        # Ensure we only attempt to read files (not directories)
        if os.path.isfile(file_path):
            print(f"Loading CV from: {file_path}")
            
            
            if file.lower().endswith(".pdf"):
                content = extract_text_from_pdf(file_path)
            else:
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # Extract owner's name from filename for metadata
            owner_name = os.path.splitext(file)[0]  
            owner_names.append(owner_name)  # Store owner name for later matching
            
           
            if content.strip():
                document = Document(content=content, metadata={"owner_name": owner_name})
                documents.append(document)
                print(f"Document created for {owner_name}")
            else:
                print(f"Skipped empty document: {file_path}")

    # Confirm the number of non-empty documents
    print(f"Loaded {len(documents)} documents for indexing.")

    if documents:
        # Create a new index from the loaded documents and persist it
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
    
   
    print("Query response:", response)
    
    
    relevant_names = []
    for owner_name in owner_names:
        if owner_name in response:  
            relevant_names.append(owner_name)
    
    
    return f"Candidates with required skills: {', '.join(relevant_names)}" if relevant_names else "No relevant information found in the documents."


rebuild_index() 


result = query_cv("I have a job description that requires Python and Django skills. Who among these candidates has these skills?")
print(result)

print(query_cv("List all skills of each candidate."))
print(query_cv("Who has experience with Python?"))
print(query_cv("Who has managed projects in AWS?"))


print(query_cv("Who has managed projects in AWS?"))