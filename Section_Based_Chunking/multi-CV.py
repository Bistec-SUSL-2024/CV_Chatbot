import os
import spacy
import pdfplumber
import json


def extract_text_from_pdf(file_path):
    """Extract text from a single PDF using pdfplumber."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def chunk_cv_with_spacy(file_path):
    """Chunk a single CV into sections using spaCy NLP."""
    # Load the spaCy language model
    nlp = spacy.load("en_core_web_sm")

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)

    # Preprocess text: remove extra spaces and normalize line breaks
    text = " ".join(text.split())

    # NLP-based section detection
    section_keywords = {
        "Personal Information": ["personal", "information", "about me", "contact"],
        "Summary": ["summary", "overview", "objective"],
        "Skills": ["skills", "technical skills", "soft skills"],
        "Work Experience": ["experience", "work history", "employment"],
        "Education": ["education", "academic background", "qualifications"],
        "Certifications": ["certifications", "training"],
        "Languages": ["languages", "language proficiency"],
        "References": ["references", "referees"],
        "Interests": ["interests", "hobbies"]
    }

    sections = {}
    current_section = "General"  # Default section if no header is detected
    sections[current_section] = ""

    # Process text line by line
    for line in text.split(". "):  # Split text into sentences/lines
        line_lower = line.lower()

        # Check if the line matches any section keywords
        matched_section = None
        for section, keywords in section_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                matched_section = section
                break

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

def process_multiple_cvs(folder_path):
    """Process all PDFs in a folder and chunk them into sections."""
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
    return results

# Example usage
folder_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local"  # Update with your folder path
cv_results = process_multiple_cvs(folder_path)

# Display results
for filename, sections in cv_results.items():
    print(f"\n== {filename} ==")
    for heading, content in sections.items():
        print(f"-- {heading} --")
        print(content[:500])  # Print the first 500 characters of content
        print("-" * 50)

with open("chunked_cvs.json", "w") as f:
    json.dump(cv_results, f, indent=4)

