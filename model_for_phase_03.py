import os
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from pinecone import Pinecone
from fuzzywuzzy import process
from openai import OpenAI
import re
import ast

load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)
embed_model = OpenAIEmbedding()
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "cv-analyzer-2"  
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
    Extracts skills, experience, and certifications from CVs
    """
    extracted_info = {
        'skills': [],
        'experience': [],
        'certifications': [],
        # 'tools': []
    }
    
    # Extract skills
    skills_match = re.findall(r'\b(?:Python|JavaScript|SQL|Azure|AWS|React|Django|Data Engineering)\b', full_text, re.IGNORECASE)
    extracted_info['skills'] = list(set(skills_match))  

    # Extract experience
    experience_match = re.findall(r'(\d+)\s+years? of experience', full_text, re.IGNORECASE)
    if experience_match:
        extracted_info['experience'] = [int(exp) for exp in experience_match]

    # Extract certifications
    certifications_match = re.findall(r'\b(?:Certified|Certification|Certifications)\b.*?[\.,;]', full_text, re.IGNORECASE)
    extracted_info['certifications'] = certifications_match

    # tools_match = re.findall(r'\b(?:Docker|Kubernetes|Terraform|Apache|Spark|Tableau|Power BI|Hadoop)\b', certification_text, re.IGNORECASE)
    # extracted_info['tools'] = list(set(tools_match))

    return extracted_info

#-------------------------------------------------Extract Mandatory Keywords------------------------------------------------


def extract_mandatory_conditions(job_description):
    """
    Use OpenAI's LLM to extract mandatory conditions (experience, skills, certifications, tools) from a refined job description.
    """
    try:
        
        prompt = f"""
        Given the following job description, extract the mandatory conditions:
        - Years of experience
        - Skills (technologies, programming languages, etc.)
        - Certifications (if any)
        - Tools (if any)

        Job Description: 
        {job_description}

        Output format:
        {{
            'years_of_experience': <years>,
            'skills': ['<skill1>', '<skill2>', ...],
            'certifications': ['<certification1>', '<certification2>', ...],
            'tools': ['<tool1>', '<tool2>', ...]
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
            'years_of_experience': mandatory_conditions.get('years_of_experience', None),
            'skills': mandatory_conditions.get('skills', []),
            'certifications': mandatory_conditions.get('certifications', []),
            'tools': mandatory_conditions.get('tools', [])
        }
        
        return mandatory_conditions
    except Exception as e:
        print(f"Error extracting mandatory conditions with LLM: {e}")
        return {
            'years_of_experience': None,
            'skills': [],
            'certifications': [],
            'tools': []
        }



#----------------------Validate-------------------------------------

def validate_cv(metadata, mandatory_conditions):
   
    # Check years of experience--------------

    required_experience = mandatory_conditions.get('years_of_experience')
    print(f"Required Experience: {required_experience}")
    
    if required_experience is not None:

        cv_experience = int(metadata.get('experience', [0])[0]) if metadata.get('experience') else 0
        
        print(f"CV Experience: {cv_experience}")
        
        if cv_experience < int(required_experience):  
            return False

    # # Check required skills-------------------

    # required_skills = set(mandatory_conditions.get('skills', []))
    # if required_skills:
    #     cv_skills = set(metadata.get('skills', []))
    #     print(f"CV Skills: {cv_skills}")
    #     if not cv_skills.issubset(required_skills):
    #         return False

    # # Check certifications--------------------

    # required_certifications = set(mandatory_conditions.get('certifications', []))
    # if required_certifications:
    #     cv_certifications = set(metadata.get('certifications', []))
    #     print(f"CV Certifications: {cv_certifications}")
    #     if not required_certifications.issubset(cv_certifications):
    #         return False
    
    # # Check Tools--------------------

    # # required_tools = set(mandatory_conditions.get('tools', []))
    # # if required_tools:
    # #     cv_tools = set(metadata.get('tools', []))
    # #     print(f"CV Tools: {cv_tools}")
    # #     if not required_tools.issubset(cv_tools):
    # #         return False

    return True


#-------------------------------------------------Rank CVs by Description------------------------------------------------

def rank_and_validate_cvs(refined_job_description, mandatory_conditions):
    """
    Rank CVs by relevance and validate them based on mandatory conditions (skills, experience, certificates).
    """
    print("Ranking CVs based on refined job description...")

    query_embedding = generate_embeddings(refined_job_description)
    if query_embedding is None:
        print("Error: Failed to generate embedding for the job description.")
        return []

    query_results = pinecone_index.query(
        vector=query_embedding,
        top_k=10, 
        include_metadata=True,
        namespace="cvs-info"
    )

    valid_cvs = []
    for match in query_results['matches']:
        metadata = match.get('metadata', {})

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

def start_chatbot_with_cv(cv_id):
    cv_text = query_cv_by_id(cv_id)
    if cv_text:
        print("Starting the chatbot with the selected CV...\n")  
        
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
                
                try:
                    index = VectorStoreIndex.from_documents([document_node], embed_model=embed_model, show_progress=False)
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
            else:
                print(f"No vectors found for CV ID {cv_id}")
                
        except Exception as e:
            print(f"Error fetching CV by ID {cv_id}: {e}")

def normalize_string(s):
    return re.sub(r"[\W_]+", "", s).lower()

#--------------------------------------------------Show CV Function-----------------------------------------------------

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
        
#-------------------------------------------------Main Section------------------------------------------------------

if __name__ == "__main__":
    
   user_input_job_description = """I have a job vacancy fpr software engineer.
    Experience required least 3 years. must have experience with python and django."""
   
   examples, instructions = retrieve_examples_and_instructions(user_input_job_description)

   if examples or instructions:
       
       refined_job_description = refine_user_prompt_with_llm(user_input_job_description, examples, instructions)
       
       print("Refined Job Description:")
       print(refined_job_description)
 
       mandatory_conditions = extract_mandatory_conditions(refined_job_description)
       print(f"Mandotary Conditions(refined JD): {mandatory_conditions}\n")
       ranked_cvs = rank_and_validate_cvs(refined_job_description, mandatory_conditions)
       
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