import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")  # Extract text from each page
    return text

if __name__ == "__main__":
    pdf_path = "Harshana-Madhuwantha-CV ( SE ).pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)
