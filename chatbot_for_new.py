import os
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Node, TextNode, Document
from pinecone import Pinecone


load_dotenv()


OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


embed_model = OpenAIEmbedding()

#
pc = Pinecone(api_key=PINECONE_API_KEY)


index_name = "cv-markdown-index"  
namespace = ""  


pinecone_index = pc.Index(index_name)

#---------------------------Generate Embeddings for job description--------------------------------------

def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

#------------------------------------CV Ranking Function--------------------------------------------------


def rank_cvs_by_description(job_description):
    print("Ranking CVs based on the job description...") 
    
    query_embedding = generate_embeddings(job_description)
    
    if query_embedding is None:
        print("Error: Failed to generate embedding for the job description.")
        return []
    
    query_results = pinecone_index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True,
        namespace=namespace
    )
    
    ranked_cvs = []
    for match in query_results['matches']:
        cv_id = match['id']
        score = match['score']
        ranked_cvs.append({
            "cv_id": cv_id,
            "score": score
        })

    ranked_cvs.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Found {len(ranked_cvs)} CVs for ranking.")  
    return ranked_cvs

#-----------------------------Function for fetch a specific CV using the ID---------------------------------------

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




#--------------------------------------Function for start a chatbot using the selected CV-------------------------------------------

def start_chatbot_with_cv(cv_id):
    cv_text = query_cv_by_id(cv_id)
    if cv_text:
        print("Starting the chatbot with the selected CV...\n")  
        
        document_node = Document(text=cv_text, doc_id=cv_id) 
        try:
            index = VectorStoreIndex.from_documents([document_node], embed_model=embed_model, show_progress=True)
            query_engine = index.as_query_engine()
            
            while True:
                question = input("\nEnter your question (or type 'exit' to quit): ")
                if question.lower() == 'exit':
                    print("Exiting the chatbot.")
                    break
                
                response = query_engine.query(question)
                print(f"Answer: {response}\n") 
        except AttributeError as e:
            print(f"Error: {e}. Please check if the document structure is compatible with VectorStoreIndex.")




if __name__ == "__main__":
    job_description = "We are looking for a project manager with experience in leading teams and managing deadlines."

    ranked_cvs = rank_cvs_by_description(job_description)
    
    if ranked_cvs:
        print("\nTop ranked CVs based on job description:")
        for idx, cv in enumerate(ranked_cvs, 1):
            print(f"{idx}. CV ID: {cv['cv_id']}, Similarity Score: {cv['score']:.4f}")
        
        selected_cv_idx = int(input("\nEnter the number of the CV you want to select: "))
        selected_cv_id = ranked_cvs[selected_cv_idx - 1]["cv_id"]
    
        start_chatbot_with_cv(selected_cv_id)
    else:
        print("No CVs found for ranking.")