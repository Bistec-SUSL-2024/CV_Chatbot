import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()


import nest_asyncio
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding  
import torch

nest_asyncio.apply()

os.environ["GROQ_API_KEY"] = "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" 


llm = Groq(model="llama3-8b-8192")
llm_70b = Groq(model="llama3-70b-8192")


embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.llm = llm
Settings.embed_model = embed_model  


documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("provide me name who has skills of python and django?")
print(response)
