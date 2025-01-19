import os
import spacy
import pdfplumber
import json
from rapidfuzz import fuzz
from concurrent.futures import ThreadPoolExecutor
import openai

# Set your OpenAI API key
openai.api_key = os.getenv("openaiKEY")

def extract_text_from_pdf(file_path):
    """Extract text from a single PDF using pdfplumber."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def preprocess_text(text):
    """Preprocess text to normalize and clean it."""
    text = text.replace("\n", " ").replace("\r", " ").strip()
    text = " ".join(text.split())  # Remove extra spaces
    return text

def detect_section(line, section_keywords):
    """Detect the section heading using fuzzy matching."""
    for section, keywords in section_keywords.items():
        for keyword in keywords:
            if fuzz.partial_ratio(line.lower(), keyword.lower()) > 80:  # Adjust threshold as needed
                return section
    return None

def refine_with_gpt(current_section, line, previous_content):
    """Refine section classification using GPT with context."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in parsing CVs into structured sections."},
                {"role": "user", "content": f"Given the current section is '{current_section}' and the previous content was: '{previous_content}', classify this line: '{line}'"}
            ],
            temperature=0
        )
        gpt_section = response["choices"][0]["message"]["content"].strip()
        return gpt_section if gpt_section else current_section
    except Exception as e:
        print(f"Error with GPT classification: {e}")
        return current_section

def chunk_cv_with_spacy(file_path):
    """Chunk a single CV into sections using spaCy NLP, fuzzy matching, and GPT for refinement."""
    # Load the spaCy language model
    nlp = spacy.load("en_core_web_sm")

    # Extract and preprocess text from the PDF
    raw_text = extract_text_from_pdf(file_path)
    text = preprocess_text(raw_text)

    # NLP-based section detection
    section_keywords = {
        "Personal Information": ["personal information", "contact", "contact details", "about me"],
        "Skills": ["skills", "technical skills", "professional skills", "expertise"],
        "Work Experience": ["work experience", "professional experience", "employment history", "career history"],
        "Education": ["education", "academic background", "qualifications", "degrees"],
        "Certifications": ["certifications", "training", "courses", "licenses"],
        "Languages": ["languages", "language proficiency", "spoken languages"],
        "References": ["references", "referees", "recommendations"],
        "Summary": ["summary", "overview", "profile", "objective"],
        "Interests": ["interests", "hobbies", "extracurricular activities"]
    }

    sections = {}
    current_section = "General"  # Default section if no header is detected
    sections[current_section] = ""
    previous_content = ""  # Track previous lines for GPT context

    for line in text.split(". "):  # Split text into sentences/lines
        line_lower = line.lower()

        # Match section using keywords
        matched_section = detect_section(line, section_keywords)

        # Use GPT if no match
        if not matched_section:
            refined_section = refine_with_gpt(current_section, line, previous_content)
        else:
            refined_section = matched_section

        # If the section changes, start a new one
        if refined_section != current_section:
            current_section = refined_section
            sections[current_section] = sections.get(current_section, "")

        # Append the line to the current section
        sections[current_section] += " " + line
        previous_content = line  # Update previous content

    # Remove extra spaces in sections
    for section in sections:
        sections[section] = sections[section].strip()

    return sections

def process_cv(file_path):
    """Process a single CV and return chunked sections."""
    try:
        return chunk_cv_with_spacy(file_path)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}

def process_multiple_cvs_parallel(folder_path, output_json_path):
    """Process all PDFs in a folder in parallel, chunk them into sections, and save as JSON."""
    results = {}

    # Get all PDF file paths
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]

    # Process PDFs in parallel
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_cv, pdf): pdf for pdf in pdf_files}
        for future in futures:
            pdf = futures[future]
            try:
                results[os.path.basename(pdf)] = future.result()
            except Exception as e:
                print(f"Error processing {pdf}: {e}")

    # Save results to JSON file
    with open(output_json_path, "w") as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Saved chunked CVs to {output_json_path}")

# Example usage
folder_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local"  # Folder containing CVs
output_json_path = r"E:\INTERN-BISTEC\CV_Chatbot\chunked_cvs.json"  # Output JSON file path

process_multiple_cvs_parallel(folder_path, output_json_path)
