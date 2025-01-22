import os
import spacy
import pdfplumber
import json
from rapidfuzz import fuzz

def extract_text_from_pdf(file_path):
    """
    Extract text from a single PDF using pdfplumber.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

def detect_section(line, section_keywords):
    """
    Detect the section heading using fuzzy matching.
    """
    for section, keywords in section_keywords.items():
        for keyword in keywords:
            if fuzz.partial_ratio(line.lower(), keyword.lower()) > 80:  # Adjust threshold as needed
                return section
    return None

def chunk_cv_with_spacy(file_path, section_keywords):
    """
    Chunk a single CV into sections using spaCy NLP and fuzzy matching.
    """
    nlp = spacy.load("en_core_web_sm")
    text = extract_text_from_pdf(file_path)
    if not text:
        raise ValueError("No text extracted from the file.")

    # Preprocess text
    text = " ".join(text.split())

    # Initialize sections dictionary
    sections = {}
    current_section = "General"
    sections[current_section] = []

    # Process text line by line
    for line in text.split(". "):  # Split text into sentences
        matched_section = detect_section(line, section_keywords)

        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []  # Initialize new section
        sections[current_section].append(line)

    # Clean up sections and join sentences
    sections = {key: " ".join(value).strip() for key, value in sections.items()}
    return sections

def process_multiple_cvs(folder_path, output_json_path):
    """
    Process all PDFs in a folder, chunk them into sections, and save as JSON.
    """
    section_keywords = {
        "Personal Information": ["personal information", "contact", "about me"],
        "Summary": ["summary", "overview", "objective"],
        "Skills": ["skills", "technical skills", "soft skills"],
        "Work Experience": ["work experience", "experience", "employment history"],
        "Education": ["education", "academic background", "qualifications"],
        "Certifications": ["certifications", "training", "courses"],
        "Languages": ["languages", "language proficiency"],
        "References": ["references", "referees"],
        "Interests": ["interests", "hobbies", "extracurricular activities"],
    }

    results = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}")
            try:
                sections = chunk_cv_with_spacy(file_path, section_keywords)
                unique_chunks = {
                    f"{filename.split('.')[0]}_{section.replace(' ', '_')}": content
                    for section, content in sections.items()
                }
                results[filename] = unique_chunks
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Save results to JSON file
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)

    print(f"Saved chunked CVs to {output_json_path}")

# Example usage
if __name__ == "__main__":
    folder_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local"  # Folder containing CVs
    output_json_path = r"E:\INTERN-BISTEC\CV_Chatbot\chunked_cvs.json"  # Output JSON file path
    process_multiple_cvs(folder_path, output_json_path)
