import os
import logging
import sys
import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from llama_index.core.schema import MetadataMode
from dotenv import load_dotenv


load_dotenv()
OpenAI_Key = os.getenv("OpenAI_Key")


# Set up logging
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s \n || %(message)s ||')


os.environ["OPENAI_API_KEY"] = OpenAI_Key

PERSIST_DIR = "./storage"


if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

def query_cv(file_path, prompt):
    if not os.path.exists(file_path):
        raise FileNotFoundError("The specified CV file was not found.")
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)

    if hasattr(response, 'some_attribute'):  # Replace with actual attribute(s)
        return {
            "content": response.some_attribute,  
            "score": response.score if hasattr(response, 'score') else None,  
        }
    else:
        return str(response)