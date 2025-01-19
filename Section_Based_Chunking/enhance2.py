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

def detect_section(line, section_keywords):
    """Detect the section heading using fuzzy matching."""
    for section, keywords in section_keywords.items():
        for keyword in keywords:
            if fuzz.partial_ratio(line.lower(), keyword.lower()) > 80:  # Adjust threshold as needed
                return section
    return None

def refine_with_gpt(current_section, line):
    """Refine section classification using GPT."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 for better context
            messages=[
                {"role": "system", "content": "You are a CV section classifier."},
                {"role": "user", "content": f"Classify this line into a section like Personal Information, Skills, Work Experience, Education, Certifications, Languages, or References: {line}"}
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

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)

    # Preprocess text: remove extra spaces and normalize line breaks
    text = " ".join(text.split())

    # NLP-based section detection
    section_keywords = {
        "Personal Information": ["personal information", "contact", "about me"],
        "Summary": ["summary", "overview", "objective"],
        "Skills": ["skills", "technical skills", "soft skills"],
        "Work Experience": ["work experience", "experience", "employment history"],
        "Education": ["education", "academic background", "qualifications"],
        "Certifications": ["certifications", "training", "courses"],
        "Languages": ["languages", "language proficiency"],
        "References": ["references", "referees"],
        "Interests": ["interests", "hobbies", "extracurricular activities"]
    }

    sections = {}
    current_section = "General"  # Default section if no header is detected
    sections[current_section] = ""

    # Process text line by line
    for line in text.split(". "):  # Split text into sentences/lines
        line_lower = line.lower()

        # Check if the line matches any section keywords
        matched_section = detect_section(line, section_keywords)

        if matched_section:
            current_section = matched_section
            sections[current_section] = sections.get(current_section, "")
        else:
            # Use GPT for classification when no match is found
            refined_section = refine_with_gpt(current_section, line)
            if refined_section != current_section:
                current_section = refined_section
                sections[current_section] = sections.get(current_section, "")
            else:
                sections[current_section] += " " + line

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
