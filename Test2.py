import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from dotenv import load_dotenv

load_dotenv()
OpenAI_Key = os.getenv("Open_ai_key")

os.environ["OPENAI_API_KEY"] = OpenAI_Key

PERSIST_DIR = "./storage"
index = None

def rebuild_index():
    global index

    
    cv_files = os.listdir("data")
    
    if not cv_files:
        print("Data directory is empty. Index will not be created.")
        
        if os.path.exists(PERSIST_DIR):
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
    else:
        
        if not os.path.exists(PERSIST_DIR):
            documents = SimpleDirectoryReader("data").load_data()  
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=PERSIST_DIR)  
        else:
            
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)

def query_cv(file_path, prompt):
    global index

    if not os.path.exists(file_path):
        raise FileNotFoundError("The specified CV file was not found.")
    
    if index is None:
        raise ValueError("Index has not been initialized. Please check the data directory or persisted storage.")

    
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)

    return str(response)

# Example usage:
rebuild_index()  # This will load up to 5 CVs from 'data' folder and store them in the index.
result = query_cv("data", "I have job description that need python and django. If there anyone who has these skills,provide his name?")
print(result)
