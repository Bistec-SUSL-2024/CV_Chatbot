import os

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, Document
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding


os.environ['OPENAI_API_KEY'] = 'cf35c7e4-43cb-4d84-8dd6-0dbd42358f33'  # SambaNova API KEY
os.environ['OPENAI_BASE_URL'] = 'https://api.sambanovacloud.com/v1'


Settings.embed_model = OpenAIEmbedding()

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model, show_progress=True)
query_engine = index.as_query_engine()
response = query_engine.query("What are the documents about?")
print(response)
