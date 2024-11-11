import os
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Set OpenAI and Pinecone API keys
OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize OpenAI embedding model
embed_model = OpenAIEmbedding()

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define index and namespace
index_name = "cv-markdown-index"  # Change to your Pinecone index name
namespace = "cv-namespace"  # Ensure this is your correct namespace

# Access the Pinecone index
pinecone_index = pc.Index(index_name)

# Function to generate embeddings using OpenAI's API for the job description
def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

# Function to rank CVs based on the job description (query)
def rank_cvs_by_description(job_description):
    # Generate the embedding for the job description
    query_embedding = generate_embeddings(job_description)
    
    if query_embedding is None:
        print("Error: Failed to generate embedding for the job description.")
        return []
    
    # Query Pinecone to find the most similar CVs
    query_results = pinecone_index.query(
        vector=query_embedding,
        top_k=5,  # Get top 5 closest matches (can adjust based on need)
        include_metadata=True,
        namespace=namespace
    )
    
    # Process the query results (sorted by score)
    ranked_cvs = []
    for match in query_results['matches']:
        cv_id = match['id']
        score = match['score']
        metadata = match['metadata']
        ranked_cvs.append({
            "cv_id": cv_id,
            "score": score,
            "metadata": metadata
        })
    
    # Sort by score (most similar CVs first)
    ranked_cvs.sort(key=lambda x: x['score'], reverse=True)
    
    return ranked_cvs

# Example usage
if __name__ == "__main__":
    job_description = "We are looking for a project manager with experience in leading teams and managing deadlines."

    # Rank CVs based on the job description
    ranked_cvs = rank_cvs_by_description(job_description)

    # Print the ranked CVs
    if ranked_cvs:
        print("Top ranked CVs based on job description:")
        for idx, cv in enumerate(ranked_cvs, 1):
            print(f"{idx}. CV ID: {cv['cv_id']}, Similarity Score: {cv['score']:.4f}")
            print(f"   CV Text Excerpt: {cv['metadata']['text'][:300]}...")  # Display a snippet of the CV text
    else:
        print("No CVs found for ranking.")
