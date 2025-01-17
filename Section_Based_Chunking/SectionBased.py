import re
import pdfplumber

def chunk_pdf_by_sections(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Example: Split by common headings
    pattern = r"(?:\n)?(?:\d+\.\s)?[A-Z][^\n]+(?:\n)+"
    sections = re.split(pattern, text)

    # Extract headings and their respective content
    headings = re.findall(pattern, text)
    chunks = dict(zip(headings, sections[1:]))

    return chunks

# Example usage
file_path = "example.pdf"
chunks = chunk_pdf_by_sections(file_path)
for heading, content in chunks.items():
    print(f"== {heading.strip()} ==")
    print(content.strip())
    print("-" * 50)
