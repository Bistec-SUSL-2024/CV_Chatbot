import re
import pdfplumber

file_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local\chef.pdf"
with pdfplumber.open(file_path) as pdf:
    for page in pdf.pages:
        print(page.extract_text())

def chunk_cv_by_sections(file_path):

    #-------------------Common section headings in CVs ---------------------------------------------------------------
    section_patterns = [
        r"Personal Information", r"Summary", r"Objective", r"Skills", r"Technical Skills",
        r"Work Experience", r"Professional Experience", r"Education", r"Certifications",
        r"Projects", r"Awards", r"Languages", r"Interests"
    ]
    # Combine patterns into a single regex
    section_regex = re.compile(r"|".join(section_patterns), re.IGNORECASE)

    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # Split by sections
    splits = re.split(section_regex, text)
    section_headings = re.findall(section_regex, text)

    # Create a dictionary of sections
    sections = {}
    for i, heading in enumerate(section_headings):
        sections[heading.strip()] = splits[i + 1].strip() if i + 1 < len(splits) else ""

    return sections

# Example usage
file_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local\chef.pdf"  # Update with your file path
sections = chunk_cv_by_sections(file_path)

# Display the chunks
if sections:
    for heading, content in sections.items():
        print(f"== {heading} ==")
        print(content[:500])  # Print the first 500 characters of content
        print("-" * 50)
else:
    print("No sections found or unable to process the file.")
