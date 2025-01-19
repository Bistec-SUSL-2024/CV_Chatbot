import os
import spacy
import pdfplumber
import json
from rapidfuzz import fuzz

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

def chunk_cv_with_spacy(file_path):
    """Chunk a single CV into sections using spaCy NLP and fuzzy matching."""
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
            # Start a new section
            current_section = matched_section
            sections[current_section] = sections.get(current_section, "")  # Initialize section if not already
        else:
            # Append the line to the current section
            sections[current_section] += " " + line

    # Remove extra spaces in sections
    for section in sections:
        sections[section] = sections[section].strip()

    return sections

def process_multiple_cvs(folder_path, output_json_path):
    """Process all PDFs in a folder, chunk them into sections, and save as JSON."""
    results = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}")
            try:
                sections = chunk_cv_with_spacy(file_path)
                results[filename] = sections
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # Save results to JSON file
    with open(output_json_path, "w") as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Saved chunked CVs to {output_json_path}")

# Example usage
folder_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local"  # Folder containing CVs
output_json_path = r"E:\INTERN-BISTEC\CV_Chatbot\chunked_cvs.json"  # Output JSON file path

process_multiple_cvs(folder_path, output_json_path)
