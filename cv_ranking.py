import os
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone

load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

embed_model = OpenAIEmbedding()

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "cv-markdown-index"  
namespace = ""  

pinecone_index = pc.Index(index_name)

def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

#-----------------------------------------------Rank CV Function-----------------------------------------------------

def rank_cvs_by_description(job_description):
    
    query_embedding = generate_embeddings(job_description)
    
    if query_embedding is None:
        print("Error: Failed to generate embedding for the job description.")
        return []
    
    try:
        query_results = pinecone_index.query(
            vector=query_embedding,
            top_k=5,  
            include_metadata=True,
            namespace=namespace
        )
    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        return []
    
    
    if not query_results.get('matches'):
        print("No matches found in Pinecone for the given job description.")
        return []

    
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
    

    ranked_cvs.sort(key=lambda x: x['score'], reverse=True)
    
    return ranked_cvs

#-----------------------------------------------------Chatbot Part---------------------------------------------------------------


def interact_with_cv(cv_id, question):
    cv_data = pinecone_index.fetch(ids=[cv_id], namespace=namespace)
    if cv_id not in cv_data["vectors"]:
        print(f"CV with ID {cv_id} not found.")
        return "CV content unavailable."

    cv_content = cv_data["vectors"][cv_id]["metadata"]["text"]

    # Generate embedding for the question
    question_embedding = generate_embeddings(question)
    if question_embedding is None:
        print("Error generating question embedding.")
        return "Unable to process the question."

    # Dummy retrieval simulation based on similarity
    # (Replace with actual QA approach, e.g., using LLM or prompt engineering for responses)
    response = f"Based on the CV, here's a response for '{question}':\n{cv_content[:300]}..."

    return response




if __name__ == "__main__":
    
    try:
        index_stats = pinecone_index.describe_index_stats(namespace=namespace)
        if index_stats['namespaces'].get(namespace, {}).get('vector_count', 0) == 0:
            print(f"No vectors found in the namespace '{namespace}'.")
    except Exception as e:
        print(f"Error accessing Pinecone index statistics: {e}")
        exit(1)

    job_description = "We are looking for a Psychologists who has experience with psychology."

    ranked_cvs = rank_cvs_by_description(job_description)

    if ranked_cvs:
        print("Top ranked CVs based on job description:")
        for idx, cv in enumerate(ranked_cvs, 1):
            print(f"{idx}. CV ID: {cv['cv_id']}, Similarity Score: {cv['score']:.4f}")
            # print(f"   CV Text Excerpt: {cv['metadata']['text'][:300]}...") 

        try:
            selected_number = int(input("\nEnter the number of the CV you want to interact with: ")) - 1
            selected_cv = ranked_cvs[selected_number]
            cv_id = selected_cv["cv_id"]
            

            print(f"\nStarting chatbot for {cv_id}'s CV...")

                
            while True:
                question = input("Ask a question (or type 'exit' to quit): ")
                if question.lower() == "exit":
                    break
                response = interact_with_cv(cv_id, question)
                print("Response:", response)

        except (IndexError, ValueError):
                print("Invalid selection.")
   
    else:
        print("No CVs found for ranking.")


