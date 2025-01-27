import os
import webbrowser
import re
import ast
from pathlib import Path
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from pinecone import Pinecone
from fuzzywuzzy import process
from openai import OpenAI
from rank_bm25 import BM25Okapi
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account


load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

SERVICE_ACCOUNT_FILE = os.getenv("Service_AP")      #------add the path to the service account file------------

SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

SOURCE_FOLDER_ID = os.getenv("G-DRIVE_CV_STORE_FOLDER_ID")


client = OpenAI(api_key=OPENAI_API_KEY)
embed_model = OpenAIEmbedding()
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "database"  
namespace = "cvs-info"  
pinecone_index = pc.Index(index_name)

#------------------------------------------------Generate Embeddings------------------------------------------------

def generate_embeddings(text):
    try:
        embedding = embed_model.get_text_embedding(text)
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None
    
#------------------------------------------------Generate Sparse Vectors------------------------------------------------

def generate_bm25_sparse_vector(texts):
    """
    Generate BM25 sparse vectors for a list of texts.

    Args:
        texts (list of str): List of texts to process.

    Returns:
        tuple: Sparse vectors and idf keys.
    """
    try:
        tokenized_corpus = [text.split() for text in texts]
        bm25 = BM25Okapi(tokenized_corpus)
        sparse_vectors = [bm25.get_scores(doc_tokens) for doc_tokens in tokenized_corpus]
        return sparse_vectors, list(bm25.idf.keys())
    except Exception as e:
        print(f"Error generating BM25 sparse vectors: {e}")
        return None, None

#-------------------------------------------------Retrieve Examples and Instructions------------------------------------------------

def retrieve_examples_and_instructions(user_input):
    """
    Retrieve relevant examples and instructions from Pinecone.
    """
    try:
        user_embedding = generate_embeddings(user_input)

        if user_embedding is None:
            print("Failed to generate user embedding.")
            return [], ""

        query_results = pinecone_index.query(
            vector=user_embedding,
            top_k=5,  
            include_metadata=True,
            namespace="examples_and_instructions"
        )

        retrieved_data = []
        instructions = None  

        for match in query_results['matches']:
            metadata = match.get('metadata', {})
            data_type = metadata.get('type', '') 

            if data_type == 'example':
                job_description = metadata.get('job_description', '')
                mandatory_keywords = metadata.get('mandatory_keywords', [])
                retrieved_data.append({
                    'job_description': job_description,
                    'mandatory_keywords': mandatory_keywords
                })
            elif data_type == 'instruction':
                instructions = metadata.get('content', '')  

        return retrieved_data, instructions
    except Exception as e:
        print(f"Error retrieving data from Pinecone: {e}")
        return [], ""

# ------------------------------------------------- Generate Combined Prompt ------------------------------------------------

def generate_combined_prompt(user_input, retrieved_data, instructions):
    """
    Generate a combined prompt using user input, job descriptions, mandatory keywords, and instructions.
    """
    combined_prompt = f"User Input: {user_input.strip()}\n\n"
    combined_prompt += "Relevant Job Descriptions and Mandatory Keywords:\n"

    for i, example in enumerate(retrieved_data, start=1):
        job_description = example.get('job_description', 'N/A').strip()
        mandatory_keywords = ', '.join(example.get('mandatory_keywords', []))
        combined_prompt += f"\nExample {i}:\n"
        combined_prompt += f"Job Description: {job_description}\n"
        combined_prompt += f"Mandatory Keywords: {mandatory_keywords}\n"

    if instructions:
        combined_prompt += f"\nInstructions:\n{instructions.strip()}\n"

    combined_prompt += "\nPlease refine the user's input based on the above examples and instructions."
    return combined_prompt

# ------------------------------------------------- Refine User Prompt with LLM ------------------------------------------------

# In-memory cache for consistency---------------------------
cache = {}

def refine_user_prompt_with_llm(user_input, examples, instructions):
    """
    Use OpenAI's LLM to refine the user's input with deterministic and consistent outputs.
    Includes caching to prevent re-generating results for the same input.
    """
    def normalize_text(input_text):
        """
        Normalize text by removing extra spaces, converting to lowercase, and ensuring consistency.
        """
        return " ".join(input_text.strip().split()).lower()

    try:
        normalized_input = normalize_text(user_input)

        # Create a unique cache key using normalized input, examples, and instructions
        cache_key = (normalized_input, tuple((ex['job_description'], tuple(ex['mandatory_keywords'])) for ex in examples), instructions)
        if cache_key in cache:
            return cache[cache_key]

        combined_prompt = generate_combined_prompt(normalized_input, examples, instructions)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly precise assistant. Always produce structured and consistent outputs based on the examples and instructions."},
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=300,
            temperature=0.0,  
            top_p=1.0  
        )

        refined_input = normalize_text(response.choices[0].message.content)

        cache[cache_key] = refined_input

        return refined_input

    except Exception as e:
        print(f"Error refining the prompt using LLM: {e}")
        return "Failed to refine the input."
    

#----------------------------------------Function for extract_skills_and_experience From CVS----------------------------------------------------

def extract_skills_and_experience(full_text):
    """
    Extract structured data (skills and years of experience) from the full_text section of a CV.
    Includes caching to prevent re-processing the same input.
    """
    def normalize_text_2(input_text):
        """
        Normalize text by removing extra spaces, converting to lowercase, and ensuring consistency.
        """
        return " ".join(input_text.strip().split()).lower()

    try:
        normalized_text_2 = normalize_text_2(full_text)

        if normalized_text_2 in cache:
            return cache[normalized_text_2]


        prompt = f"""

        Given the following full_text,
        - Job_Title (remove Just get the title. remove words like junior, senior and etc. Ex: If prompt say senior engineer, remove senior word and just extract engineer.)

        Given the following full_text, extract the following details ONLY from the 'skills' section:
        - Skills (technologies, programming languages, etc)
         
        Given the following full_text, extract the following details:
        - Identify date ranges for job experience in the format 'YYYY-MM to YYYY-MM' or similar. 
        - If no end date is provided, assume it is the current date.
        - Calculate the total years of experience from these date ranges and provide it as an integer.
       
        Please ignore other sections like education or personal information when calculating total years of experience. 
        

        Ensure the output format is:
        {{  
            'job_title': <job_title>,
            'years_of_experience': <integer>,
            'skills': ['<skill1>', '<skill2>', ...],
        }}

        full_text: 
        {full_text}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that extracts structured data from CV text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.0,
            top_p=1.0
        )

        response_message = response.choices[0].message.content.strip()

        # Validate response format
        if not response_message.startswith("{") or not response_message.endswith("}"):
            print("Invalid response format:", response_message)
            return {
                'job_title': [],
                'years_of_experience': 0,
                'skills': []
            }

        # Parse response safely
        try:
            user_conditions = ast.literal_eval(response_message)
        except (SyntaxError, ValueError) as e:
            print(f"Error parsing response: {e}")
            return {
                'years_of_experience': 0,
                'skills': []
            }

        # Prepare the structured output
        extracted_info = {
            'job_title': user_conditions.get('job_title', []),
            'years_of_experience': int(user_conditions.get('years_of_experience', 0)),
            'skills': user_conditions.get('skills', [])
        }

        # Save the result in cache
        cache[normalized_text_2] = extracted_info

        return extracted_info

    except Exception as e:
        print(f"Error extracting skills and experience: {e}")
        return {
            'job_title': [],
            'years_of_experience': 0,
            'skills': []
        }


#-------------------------------------------------Extract Mandatory Keywords------------------------------------------------


def extract_mandatory_conditions(job_description):
    """
    Use OpenAI's LLM to extract mandatory conditions (experience, skills, certifications, tools) from a refined job description.
    """
    try:
        
        prompt = f"""
        Given the following job description, extract the mandatory conditions:
        - Job title
        - Years of experience(If years of experience not included in users prompt set it as 0)
        - Skills (technologies, programming languages, etc. If skills are not mentioned in user prompt set it as [])
        - Certifications (if any)
        - Tools (if any)

        Job Description: 
        {job_description}

        Output format:
        {{
            'job_title' : <job_title>,
            'years_of_experience': <years>,
            'skills': ['<skill1>', '<skill2>', ...],
            'certifications': ['<certification1>', '<certification2>', ...],
            'tools': ['<tool1>', '<tool2>', ...],

        }}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "system", "content": "You are an assistant that extracts mandatory conditions from job descriptions."},
                      {"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.0,  
            top_p=1.0  
        )

        response_message = response.choices[0].message.content.strip()
        mandatory_conditions = ast.literal_eval(response_message)

        mandatory_conditions = {
            'job_title': mandatory_conditions.get('job_title', []),
            'years_of_experience': mandatory_conditions.get('years_of_experience', None),
            'skills': mandatory_conditions.get('skills', []),
            'certifications': mandatory_conditions.get('certifications', []),
            'tools': mandatory_conditions.get('tools', [])
        }

        key_words_for_search = list(mandatory_conditions.values())
        flattened_list = [key_words_for_search[0]] + [key_words_for_search[1]]+ [skill for sublist in key_words_for_search[2:] for skill in sublist]
        print(f"Mandatory keywords : {mandatory_conditions}")
        
        return mandatory_conditions, flattened_list
    
    except Exception as e:
        print(f"Error extracting mandatory conditions with LLM: {e}")
        return {
            'job_title': [],
            'years_of_experience': None,
            'skills': [],
            'certifications': [],
            'tools': []
        }



#----------------------Validate-------------------------------------

def validate_cv(extracted_info_from_user, mandatory_conditions):


    def normalize_text(input_text):
        """
        Normalize text by removing extra spaces, converting to lowercase, and ensuring consistency.
        """
        return " ".join(input_text.strip().split()).lower()

    def normalize_skills(skills):
        """
             Normalize a list of skills using the normalize_text function.
        """
        return set(normalize_text(skill) for skill in skills)
    

    # check job_title------------------------

    required_job_title = set(mandatory_conditions.get('job_title', []))
    required_job_title = normalize_text(mandatory_conditions.get('job_title', []))
    if required_job_title:
        cv_job_title = set(extracted_info_from_user.get('job_title', []))
        cv_job_title = normalize_text(extracted_info_from_user.get('job_title', []))
        if not (required_job_title in cv_job_title):
            print("No matching job titles....")
            return False
   
    # Check years of experience--------------

    required_experience = mandatory_conditions.get('years_of_experience')
    print(f"Required Experience: {required_experience}")
    
    if required_experience is not None:

        cv_experience = extracted_info_from_user.get('years_of_experience', 0)
        
        print(f"CV Experience: {cv_experience}")
        
        if cv_experience < int(required_experience):
            print("Experience isn't enough....")  
            return False

    # Check required skills-------------------

    required_skills = set(mandatory_conditions.get('skills', []))
    required_skills = normalize_skills(mandatory_conditions.get('skills', []))
    if required_skills:
        cv_skills = set(extracted_info_from_user.get('skills', []))
        cv_skills = normalize_skills(extracted_info_from_user.get('skills', []))
        if not required_skills & cv_skills:
            print("No matching skills....")
            return False

    # # Check certifications--------------------

    # required_certifications = set(mandatory_conditions.get('certifications', []))
    # if required_certifications:
    #     cv_certifications = set(extracted_info_from_user.get('certifications', []))
    #     print(f"CV Certifications: {cv_certifications}")
    #     if not required_certifications.issubset(cv_certifications):
    #         return False
    
    # # Check Tools--------------------

    # required_tools = set(mandatory_conditions.get('tools', []))
    # if required_tools:
    #     cv_tools = set(extracted_info_from_user.get('tools', []))
    #     print(f"CV Tools: {cv_tools}")
    #     if not required_tools.issubset(cv_tools):
    #         return False

    return True


#-------------------------------------------------Rank CVs by Description------------------------------------------------

def rank_and_validate_cvs(refined_job_description, mandatory_conditions, mandatory_keywords):
    """
    Rank CVs by relevance and validate them based on mandatory conditions (skills, experience, certificates).
    """
    print("Ranking CVs based on refined job description...")


    # Convert all items in the list to strings
    query_texts = [str(item) for item in mandatory_keywords]

    query_sparse_vector, idf_keys = generate_bm25_sparse_vector(query_texts)

    if query_sparse_vector is None:
        raise ValueError("Failed to generate sparse vectors for the query.")

    # Use the first sparse vector from the query
    query_vector = query_sparse_vector[0]

    # Convert the NumPy array to a Python list for Pinecone
    query_sparse = {
            "indices": list(range(len(query_vector))),
            "values": query_vector.tolist()  # Convert ndarray to list
        }

    query_embedding = generate_embeddings(refined_job_description)
    if query_embedding is None:
        print("Error: Failed to generate embedding for the job description.")
        return []
    
    hdense, hsparse = hybrid_score_norm(query_embedding, query_sparse, alpha=0.20)

    query_results = pinecone_index.query(
        vector=hdense,
        sparse_vector=hsparse,
        top_k=10, 
        include_metadata=True,
        namespace="cvs-info"
    )

    valid_cvs = []
    for match in query_results['matches']:
        metadata = match.get('metadata', {})
        # print(f"metadata : {metadata}")

        extracted_info = extract_skills_and_experience(metadata.get('text', ''))
        print(f"\nCV's Info: {extracted_info}")
        
        is_valid = validate_cv(extracted_info, mandatory_conditions)

        if is_valid:
            valid_cvs.append({
                "cv_id": match['id'],
                "score": match['score'],
                "metadata": metadata,
                "extracted_info": extracted_info  
            })

    valid_cvs.sort(key=lambda x: x['score'], reverse=True)  
    print(f"Found {len(valid_cvs)} valid CVs based on the job description.")

    return valid_cvs


#------------------ Function For Hybrid Algorithm--------------------------------

def hybrid_score_norm(dense, sparse, alpha: float):
    """Hybrid score using a convex combination

    alpha * dense + (1 - alpha) * sparse

    Args:
        dense: Array of floats representing
        sparse: a dict of `indices` and `values`
        alpha: scale between 0 and 1
    """
    if alpha < 0 or alpha > 1:
        raise ValueError("Alpha must be between 0 and 1")
    hs = {
        'indices': sparse['indices'],
        'values':  [v * (1 - alpha) for v in sparse['values']]
    }
    return [v * alpha for v in dense], hs


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

# def start_chatbot_with_cv(cv_id):
#     cv_text = query_cv_by_id(cv_id)
#     if cv_text:
#         print("Starting the chatbot with the selected CV...\n")  
        
#         try:
#             fetch_response = pinecone_index.fetch(ids=[cv_id], namespace=namespace)
            
#             if 'vectors' in fetch_response and cv_id in fetch_response['vectors']:
#                 cv_metadata = fetch_response['vectors'][cv_id]['metadata']
#                 cv_embedding = fetch_response['vectors'][cv_id]['values']  
                
#                 document_node = Document(
#                     text=cv_text,
#                     doc_id=cv_id,
#                     embedding=cv_embedding  
#                 )
                
#                 try:
#                     index = VectorStoreIndex.from_documents([document_node], embed_model=embed_model, show_progress=False)
#                     query_engine = index.as_query_engine()
                    
#                     while True:
#                         question = input("\nEnter your question (or type 'exit' to quit): ")
#                         if question.lower() == 'exit':
#                             print("Exiting the chatbot.")
#                             break
                        
#                         response = query_engine.query(question)
#                         print(f"Answer: {response}\n")
#                 except AttributeError as e:
#                     print(f"Error: {e}. Please check if the document structure is compatible with VectorStoreIndex.")
#             else:
#                 print(f"No vectors found for CV ID {cv_id}")
                
#         except Exception as e:
#             print(f"Error fetching CV by ID {cv_id}: {e}")

#-----------------use to integrate with front_end---------------------to run only backend use above code and comment this part--------#

def start_chatbot_with_cv(cv_id, question):
    cv_text = query_cv_by_id(cv_id)
    if cv_text:
        try:
    
            fetch_response = pinecone_index.fetch(ids=[cv_id], namespace=namespace)
            
            if 'vectors' in fetch_response and cv_id in fetch_response['vectors']:
                cv_metadata = fetch_response['vectors'][cv_id]['metadata']
                cv_embedding = fetch_response['vectors'][cv_id]['values']  
                
                document_node = Document(
                    text=cv_text,
                    doc_id=cv_id,
                    embedding=cv_embedding
                )
                
                index = VectorStoreIndex.from_documents([document_node], embed_model=embed_model, show_progress=False)
                query_engine = index.as_query_engine()

                response = query_engine.query(question)
                return str(response) 

            else:
                return "Error: No vectors found for the provided CV."
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return "Error: CV not found."



def normalize_string(s):
    return re.sub(r"[\W_]+", "", s).lower()

#--------------------------------------------------Show CV Function-----------------------------------------------------

def show_cv(cv_id):
    print(f"Searching for the original CV with ID '{cv_id}'...")

    normalized_cv_id = normalize_string(cv_id)

    try:
        # Search for files in the Google Drive folder
        query = f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/pdf'"
        results = drive_service.files().list(
            q=query, fields="files(id, name, webViewLink)"
        ).execute()
        files = results.get('files', [])

        if not files:
            print("Error: No files found in the Google Drive folder.")
            return {"success": False, "message": "No files found in the Google Drive folder."}

        normalized_filenames = [(normalize_string(file['name'].rsplit('.', 1)[0]), file) for file in files]

        best_match = process.extractOne(normalized_cv_id, [filename[0] for filename in normalized_filenames])

        if best_match and best_match[1] >= 80:
            matched_file = next(file for name, file in normalized_filenames if name == best_match[0])

            file_name = matched_file['name']
            web_view_link = matched_file['webViewLink']

            print(f"Found CV: {file_name}")
            print(f"Opening CV '{file_name}' in browser...")

            # Open the file in the default web browser
            webbrowser.open(web_view_link)

            return {"success": True, "message": f"Opened CV '{file_name}' successfully in the browser."}

        else:
            print(f"No matching CV PDF found for ID '{cv_id}'.")
            return {"success": False, "message": f"No matching CV PDF found for ID '{cv_id}'."}

    except Exception as e:
        print(f"Error accessing Google Drive or processing files: {e}")
        return {"success": False, "message": f"Error accessing Google Drive: {e}"}
        
#-------------------------------------------------Main Section------------------------------------------------------

if __name__ == "__main__":
    
   user_input_job_description = """I have a job vacancy for a maintenance technician. experience at least 1 years.
    """
   
   examples, instructions = retrieve_examples_and_instructions(user_input_job_description)

   if examples or instructions:
       
       refined_job_description = refine_user_prompt_with_llm(user_input_job_description, examples, instructions)
       
       print("Refined Job Description:")
       print(refined_job_description)
 
       mandatory_conditions, keywords = extract_mandatory_conditions(refined_job_description)
       ranked_cvs = rank_and_validate_cvs(refined_job_description, mandatory_conditions, keywords)
       
       if ranked_cvs:
           print("\nTop ranked CVs based on refined job description:")
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
   else:
       print("No relevant examples or instructions found.")