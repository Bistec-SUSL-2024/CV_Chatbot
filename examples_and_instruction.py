import os
from pinecone import Index, ServerlessSpec
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

examples_namespace = "job_description_examples"


#-----------------------------------------------Create Pinecone Index-----------------------------------------------------

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "test-db"
namespace = examples_namespace
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

#-------------------------------------------------Examples & Instructions--------------------------------------------------

examples = [
    {
        "job_description": "We need a Software Engineer with 3+ years of experience in Python and Django. Must have knowledge of REST APIs and familiarity with PostgreSQL. Candidates without these skills will not be considered.",
        "mandatory_keywords": ['software engineer', '3+ years', 'python', 'django', 'rest apis', 'postgresql']
    },
    {
        "job_description": "Seeking a Data Scientist with expertise in machine learning algorithms, 5+ years of experience, and proficiency in Python, TensorFlow, and PyTorch. Preferred experience with AWS or GCP.",
        "mandatory_keywords": ['data scientist', 'machine learning algorithms', '5+ years', 'python', 'tensorflow', 'pytorch', 'aws', 'gcp']
    },
    {
        "job_description": "Looking for a Project Manager with PMP certification and 7+ years of experience leading cross-functional teams. Expertise in Agile methodologies is mandatory.",
        "mandatory_keywords": ['project manager', 'pmp certification', '7+ years', 'cross-functional teams', 'agile methodologies']
    }
]

instructions = """
Refine the following job description to:
1. Improve specificity by highlighting key responsibilities.
2. Ensure alignment with required skills and experience.
3. Extract mandatory requirements and exclude candidates who do not meet them.

Mandatory Keywords to Extract:
- Job Role
- Years of Experience
- Core Technologies or Skills
- Certifications (if any)
"""

#----------------------------------Function For Store Examples & Instructions in Pinecone--------------------------------------

def check_existence_in_pinecone(ids, namespace):
    try:
        fetch_response = pinecone_index.fetch(ids=ids, namespace=namespace)
        return fetch_response.get("vectors", {})
    except Exception as e:
        print(f"Error checking existence in Pinecone: {e}")
        return {}

def store_examples_and_instructions_with_check():
    
    instruction_id = "instructions"
    existing_vectors = check_existence_in_pinecone([instruction_id], examples_namespace)
    
    if instruction_id not in existing_vectors:
        print("Instructions do not exist. Adding to Pinecone...")
        instruction_embedding = embed_model.get_text_embedding(instructions)
        pinecone_index.upsert([
            {
                "id": instruction_id,
                "values": instruction_embedding,
                "metadata": {"type": "instruction", "content": instructions}
            }
        ], namespace=examples_namespace)
    else:
        print("Instructions already exist in Pinecone. Skipping upsert.")

    # Check and store examples
    for i, example in enumerate(examples):
        example_id = f"example_{i+1}"
        existing_vectors = check_existence_in_pinecone([example_id], examples_namespace)
        
        if example_id not in existing_vectors:
            print(f"Example {i+1} does not exist. Adding to Pinecone...")
            example_embedding = embed_model.get_text_embedding(example["job_description"])
            pinecone_index.upsert([
                {
                    "id": example_id,
                    "values": example_embedding,
                    "metadata": {
                        "type": "example",
                        "job_description": example["job_description"],
                        "mandatory_keywords": example["mandatory_keywords"]
                    }
                }
            ], namespace=examples_namespace)
        else:
            print(f"Example {i+1} already exists in Pinecone. Skipping upsert.")

store_examples_and_instructions_with_check()
