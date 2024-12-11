import os
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OpenAI_Key")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


embed_model = OpenAIEmbedding()


client = OpenAI(api_key=OPENAI_API_KEY)


embed_model = OpenAIEmbedding()

def refine_user_prompt_with_llm(user_input, examples, instructions):
    """
    Use OpenAI's LLM to refine the user's input based on the provided examples and instructions.
    """
    try:
        # Create a combined prompt using the examples and instructions
        combined_prompt = (
            f"User Input: {user_input}\n\n"
            "Examples:\n"
        )
        
        for example in examples:
            combined_prompt += (
                f"Job Description: {example['job_description']}\n"
                f"Mandatory Keywords: {', '.join(example['mandatory_keywords'])}\n\n"
            )
        
        combined_prompt += f"Instructions:\n{instructions}\n"
        combined_prompt += "Please refine the user's input based on the above examples and instructions."

        # Call the OpenAI API to get a refined response using the new interface
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Specify the model to use
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=150, # Limit the number of tokens in the response
            temperature=0.2 
            
        )

        # Extract and return the generated text from the response
        refined_input = response.choices[0].message.content  # Corrected access method
        return refined_input

    except Exception as e:
        print(f"Error refining the prompt using LLM: {e}")
        return "Failed to refine the input."

if __name__ == "__main__":
    # User input
    user_input = "I need someone with experience in data engineering and Azure tools. Experience at least 1 year"
    
    # List of example job descriptions as dictionaries
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

    # Instructions for refining job descriptions
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

    # Refine the user's prompt using the examples and instructions
    refined_input = refine_user_prompt_with_llm(user_input, examples, instructions)

    print("Refined Input:")
    print(refined_input)