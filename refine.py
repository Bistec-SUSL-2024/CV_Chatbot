import os
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
from pinecone import Pinecone  # Correct import for Pinecone
from llama_index.llms.openai import OpenAI
from llama_index.legacy import LLMPredictor

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Initialize embedding model
embed_model = OpenAIEmbedding()

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)


index_name = "cv-markdown-index-3"  
namespace = "job_description_examples"  
pinecone_index = pc.Index(index_name)# Correct way to initialize the index

def generate_embeddings(text):
    """Generate embeddings for given text using OpenAI's embedding model."""
    embed_model = OpenAIEmbedding()  # Ensure this is correctly set up
    try:
        embedding = embed_model.get_text_embedding(text)
        # print(f"Generated embedding for input '{text}': {embedding}")  # Debug print
        return embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

def retrieve_examples_and_instructions(user_input):
    """
    Retrieve relevant examples and instructions from Pinecone.
    """
    try:
        # Generate embeddings for the user input
        user_embedding = generate_embeddings(user_input)

        if user_embedding is None:
            print("Failed to generate user embedding.")
            return []

        # Query Pinecone for relevant examples and instructions
        query_results = pinecone_index.query(
            vector=user_embedding,
            top_k=1,  # Retrieve top 3 matches
            include_metadata=True,
            namespace=namespace
        )

        print(query_results)
        # print(f"Query results: {query_results}")  # Debug print
        retrieved_data = []
        instructions = None
        for match in query_results['matches']:
            metadata = match.get('metadata', {})
            job_description = metadata.get('job_description', '')
            mandatory_keywords = metadata.get('mandatory_keywords', [])
            
            # Append both job description and keywords as a dictionary
            retrieved_data.append({
                'job_description': job_description,
                'mandatory_keywords': mandatory_keywords
            })
 
        return retrieved_data
    

    except Exception as e:
        print(f"Error retrieving data from Pinecone: {e}")
        return []
    

def generate_combined_prompt(user_input, retrieved_data):
    """
    Generate a combined prompt using user input, job descriptions, and mandatory keywords.
    """
    combined_prompt = f"User Input: {user_input}\n\n"
    combined_prompt += "Relevant Job Descriptions and Mandatory Keywords:\n"
    
    for i, example in enumerate(retrieved_data, start=1):
        combined_prompt += f"\nExample {i}:\n"
        combined_prompt += f"Job Description: {example['job_description']}\n"
        combined_prompt += f"Mandatory Keywords: {', '.join(example['mandatory_keywords'])}\n"

    combined_prompt += "\nPlease refine the user's input based on the above examples."
    return combined_prompt



def refine_user_prompt_with_llm(combined_prompt):
    """
    Use an LLM to refine the user's input based on the combined prompt.
    """
    try:
        # Initialize OpenAI model with necessary parameters
        llm_instance = OpenAI(temperature=0)  # Adjust parameters as needed
        
        # Ensure llm_instance is created properly
        if not isinstance(llm_instance, OpenAI):
            raise TypeError("Expected an instance of OpenAI")

        # Initialize LLMPredictor with the LLM instance
        llm_predictor = LLMPredictor(llm=llm_instance)

        # Debugging: Print out combined prompt before sending it to LLM
        print("Combined Prompt:")
        print(combined_prompt)

        # Use predict method correctly
        response = llm_predictor.predict(combined_prompt)
        
        return response
    except Exception as e:
        print(f"Error refining the prompt using LLM: {e}")
        return "Failed to refine the input."


if __name__ == "__main__":
    user_input = "I have a job vacancy, that needs skills in Azure Data Engineering tools. Experience required least 5 years"

    # Step 1: Retrieve relevant examples and instructions from Pinecone
    retrieved_data = retrieve_examples_and_instructions(user_input)

    if not retrieved_data:
        print("No relevant examples or instructions found.")
    else:
      
        combined_prompt = generate_combined_prompt(user_input, retrieved_data)

        # Debugging: Print out the combined prompt before sending it to LLM
        # print("Combined Prompt:")
        # print(combined_prompt)
        
        print(f"Type of combined_prompt: {type(combined_prompt)}")

        # Step 3: Refine the user's input using LLM
        refined_input = refine_user_prompt_with_llm(combined_prompt)

        print("Refined Input:")
        print(refined_input)