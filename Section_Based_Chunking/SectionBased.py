import openai
import pdfplumber

# Set your OpenAI API key
openai.api_key = "your-openai-api-key"

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def chunk_cv_with_openai(text):
    prompt = f"""
    The following is the text extracted from a CV. Divide the CV into structured sections like "Personal Information," 
    "Skills," "Work Experience," "Education," "Certifications," "Languages," and "References." If a section is missing, skip it. 
    Output the result as a JSON object with the section names as keys and the corresponding content as values.

    CV Text:
    {text}
    
    JSON Format Output:
    """
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use a suitable GPT model
        prompt=prompt,
        max_tokens=2000,
        temperature=0
    )
    return response["choices"][0]["text"].strip()

# Example usage
file_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local\chef.pdf"  # Update with your file path
cv_text = extract_text_from_pdf(file_path)
chunked_cv = chunk_cv_with_openai(cv_text)

# Print the chunked sections
print(chunked_cv)
