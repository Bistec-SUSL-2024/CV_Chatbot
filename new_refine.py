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

def refine_user_prompt_with_llm(user_input, example):
    """
    Use OpenAI's LLM to refine the user's input based on the provided example.
    """
    try:
        
        combined_prompt = (
            f"User Input: {user_input}\n"
            f"Example Job Description: {example}\n"
            "Please refine the user's input based on the above example."
        )

        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=150  
        )

        
        refined_input = response.choices[0].message.content  
        return refined_input

    except Exception as e:
        print(f"Error refining the prompt using LLM: {e}")
        return "Failed to refine the input."

if __name__ == "__main__":
    # User input
    user_input = "I need someone with experience in data engineering and Azure tools."
    
    example_job_description = (
        "We are looking for a Data Engineer with at least 5 years of experience in Azure Data Factory, "
        "Azure Databricks, and data pipeline development."
    )

    refined_input = refine_user_prompt_with_llm(user_input, example_job_description)

    print("Refined Input:")
    print(refined_input)