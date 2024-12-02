import os
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Node, Document
from pinecone import Pinecone
from fuzzywuzzy import process
from fastapi import HTTPException
import re


load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


embed_model = OpenAIEmbedding()
pc = Pinecone(api_key=PINECONE_API_KEY)


index_name = "cv-markdown-index-3"  
namespace = ""  
pinecone_index = pc.Index(index_name)

#------------------------------------------------Generate Embeddings------------------------------------------------

def generate_embeddings(text):
    """Generate embeddings for given text using the embedding model."""
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

def refine_job_description(raw_description):
    """
    Refine the input job description by adding helpful structure and guidance.
    """
    refined_prompt = f"""
    Refine the following job description to improve specificity, highlight key responsibilities, and ensure alignment with required skills and experience. 
    Additionally, exclude any candidates who do not meet the mandatory requirements specified in the description.
    "{raw_description.strip()}"

    Examples:
    Input: "We are looking for a project manager with experience in leading teams and managing deadlines."
    Output: "Seeking an experienced Project Manager to lead cross-functional teams, manage timelines, and ensure project delivery. 
    Requirements: 5+ years of experience in Agile/Scrum methodologies, strong leadership skills, and a PMP certification (preferred)."

    Input: "We are looking for a data scientist with knowledge of Python and machine learning."
    Output: "Hiring a Data Scientist with 3+ years of experience in Python, machine learning algorithms, and data preprocessing. 
    Must have expertise in frameworks such as TensorFlow or PyTorch. Preferred: Experience in cloud-based ML solutions (AWS or Azure). 
    Candidates without Python and ML experience will not be considered."

    Input: "We need a software developer."
    Output: "Looking for a Software Developer with expertise in full-stack development. 
    Must have 3+ years of experience with JavaScript, React, Node.js, and familiarity with database systems (SQL/NoSQL). 
    Responsibilities include building scalable applications and collaborating with product teams.PMP certification or equivalent is mandatory. 
    Candidates without leadership experience or certifications will not be considered."

    Here's how to improve it:
    1. Mention specific skills required (e.g., Python, data analysis, leadership, etc.).
    2. Specify years of experience and any certifications (e.g., PMP, CPA).
    3. Outline the primary responsibilities (e.g., manage a team, oversee budgets).
    4. Highlight soft skills (e.g., communication, problem-solving).

    Ensure the job description includes these details for better matching.
    """
    return refined_prompt

#-------------------------------------------------Rank CV Function------------------------------------------------

# def rank_cvs_by_description(job_description):
#     print("Ranking CVs based on the job description...") 
    
#     query_embedding = generate_embeddings(job_description)
    
    
#     if query_embedding is None:
#         print("Error: Failed to generate embedding for the job description.")
#         return []
    
#     query_results = pinecone_index.query(
#         vector=query_embedding,
#         top_k=5,
#         include_metadata=True,
#         namespace=namespace
#     )
    
#     ranked_cvs = []
#     for match in query_results['matches']:
#         cv_id = match['id']
#         score = match['score']
#         ranked_cvs.append({
#             "cv_id": cv_id,
#             "score": score
#         })

#     ranked_cvs.sort(key=lambda x: x['score'], reverse=True)
    
#     print(f"Found {len(ranked_cvs)} CVs for ranking.")  
#     return ranked_cvs

def rank_cvs_by_description(job_description):
    """Rank CVs based on the provided job description."""
    print("Ranking CVs based on the job description...") 
    
    # Refine the job description
    refined_description = refine_job_description(job_description)
    print("Refined Job Description:")
    print(refined_description)
    
    query_embedding = generate_embeddings(refined_description)
    
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
    
    mandatory_keywords = extract_mandatory_keywords(refined_description)
    print(f"Mandatory Keywords: {mandatory_keywords}")

    ranked_cvs = []
    for match in query_results['matches']:
        metadata = match['metadata']
        cv_text = metadata.get("text", "").lower()
        if all(keyword.lower() in cv_text for keyword in mandatory_keywords):
            cv_id = match['id']
            score = match['score']
            ranked_cvs.append({
                "cv_id": cv_id,
                "score": score,    
            })

    ranked_cvs.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Found {len(ranked_cvs)} CVs for ranking.")  
    return ranked_cvs

#----------------------------------------Mandatory Keywords Function-------------------------------------------------

def extract_mandatory_keywords(refined_description):
    """
    Extract mandatory requirements from the refined job description.
    For simplicity, we assume that requirements follow phrases like 'must have', 'required', etc.
    """
    mandatory_keywords = []
    lines = refined_description.splitlines()

    for line in lines:
        # Focus on lines with phrases like "must have" or "required"
        if any(phrase in line.lower() for phrase in ["must have", "required", "mandatory"]):
            # Extract key phrases (skills, certifications, etc.)
            phrases = re.findall(r"[A-Za-z0-9+.\- ]+", line)
            mandatory_keywords.extend(phrases)
    
    # Deduplicate and filter out generic terms
    filtered_keywords = [kw.strip().lower() for kw in set(mandatory_keywords)]
    ignore_words = {"the", "and", "or", "with", "in", "to", "of", "is", "as", "e.g.", "include"}
    final_keywords = [kw for kw in filtered_keywords if kw not in ignore_words and len(kw) > 1]
    
    return final_keywords

#-------------------------------------------------CV Selection Function-----------------------------------------------------------

def query_cv_by_id(cv_id):
    print(f"Fetching details for CV ID {cv_id}...")  
    
    try:
        fetch_response = pinecone_index.fetch(ids=[cv_id], namespace=namespace)
        
        if 'vectors' in fetch_response and cv_id in fetch_response['vectors']:
            cv_metadata = fetch_response['vectors'][cv_id]['metadata']
            cv_text = cv_metadata['text']
            return cv_text
        else:
            print(f"No CV found with ID {cv_id}")
            return None
    except Exception as e:
        print(f"Error fetching CV by ID {cv_id}: {e}")
        return None

#-----------------------------------------------Chat_bot Function-------------------------------------------------------


def start_chatbot_with_cv(cv_id, question):
    try:
        cv_text = query_cv_by_id(cv_id)
        if cv_text:
            print(f"Starting the chatbot with the selected CV...")  
            
            # Fetch the CV from Pinecone
            fetch_response = pinecone_index.fetch(ids=[cv_id], namespace=namespace)
            if 'vectors' in fetch_response and cv_id in fetch_response['vectors']:
                cv_metadata = fetch_response['vectors'][cv_id]['metadata']
                cv_embedding = fetch_response['vectors'][cv_id]['values']  
                cv_text = cv_metadata['text']
                
                document_node = Document(
                    text=cv_text,
                    doc_id=cv_id,
                    embedding=cv_embedding  
                )
                
                index = VectorStoreIndex.from_documents([document_node], embed_model=embed_model, show_progress=False)
                query_engine = index.as_query_engine()

                response = query_engine.query(question)
                return {"answer": str(response)}  
                
            else:
                raise HTTPException(status_code=404, detail="No vectors found for CV ID")
        else:
            raise HTTPException(status_code=404, detail="CV not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#--------------------------------------------------Show CV Function-----------------------------------------------------


def normalize_string(s):
    # Normalizes a string for comparison
    return re.sub(r"[\W_]+", "", s).lower()

def show_cv(cv_id):
    print(f"Searching for the original CV with ID '{cv_id}'...")

    normalized_cv_id = normalize_string(cv_id)

    data_folder = Path("./data")
    if not data_folder.exists():
        print("Error: 'data' folder does not exist.")
        return {"success": False, "message": "Data folder does not exist."}
    
    pdf_files = list(data_folder.glob("*.pdf"))

    normalized_filenames = [(normalize_string(file.stem), file) for file in pdf_files]

    best_match = process.extractOne(normalized_cv_id, [filename[0] for filename in normalized_filenames])

    if best_match and best_match[1] >= 80: 
        matched_file = next(file for name, file in normalized_filenames if normalize_string(file.stem) == best_match[0])
        print(f"Found CV: {matched_file}")
        
        try:
            webbrowser.open(matched_file.resolve().as_uri())
            print(f"Opening CV '{matched_file.name}'...")
            return {"success": True, "message": f"Opened CV '{matched_file.name}' successfully."}
        except Exception as e:
            print(f"Error opening CV PDF: {e}")
            return {"success": False, "message": f"Error opening CV: {e}"}
    else:
        print(f"No matching CV PDF found for ID '{cv_id}'.")
        return {"success": False, "message": f"No matching CV PDF found for ID '{cv_id}'."}

#-------------------------------------------------Main Section------------------------------------------------------

if __name__ == "__main__":
    job_description = """I have a job vacancy, that needs skills in Azure Data Engineering tools.
    Experience required least 5 years."""

    ranked_cvs = rank_cvs_by_description(job_description)
    
    if ranked_cvs:
        print("\nTop ranked CVs based on job description:")
        for idx, cv in enumerate(ranked_cvs, 1):
            print(f"{idx}. CV ID: {cv['cv_id']}, Similarity Score: {cv['score']:.4f}")
        
        selected_cv_idx = int(input("\nEnter the number of the CV you want to select: "))
        selected_cv_id = ranked_cvs[selected_cv_idx - 1]["cv_id"]
    
        show_original = input("Would you like to view the original CV PDF? (yes/no): ").strip().lower()
        if show_original in ["yes", "y"]:
            show_cv(selected_cv_id)

        start_chatbot_with_cv(selected_cv_id)
    else:
        print("No CVs found for ranking.")
