import os
import spacy
import pdfplumber
import json
import re
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone using the new way
pinecone_api_key = os.getenv("pineconeAPI")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

# Create Pinecone client
pc = Pinecone(api_key=pinecone_api_key, environment=pinecone_environment)

# Create a Pinecone index if it doesn't exist
index_name = "test-3"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # dimension should match your embedding model
        metric='cosine',  # you can choose other metrics like 'euclidean'
        spec=ServerlessSpec(
            cloud='aws',
            region='us-west-2'  # Change this as per your desired region
        )
    )
index = pc.Index(index_name)  # Access the created index

# Load the sentence transformer model for embedding generation
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # or any other model you'd like

def extract_text_from_pdf(file_path):
    """Extract text from a single PDF using pdfplumber."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def detect_section(line, section_keywords, nlp):
    """Detect the section heading using fuzzy matching and NER for improved accuracy."""
    for section, keywords in section_keywords.items():
        for keyword in keywords:
            # Fuzzy matching with a lowered threshold for better precision
            if fuzz.partial_ratio(line.lower(), keyword.lower()) > 85:  # Adjust threshold
                return section
    return None

def chunk_cv_with_spacy(file_path):
    """Chunk a single CV into sections using spaCy NLP and fuzzy matching with better context handling."""
    nlp = spacy.load("en_core_web_sm")

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)

    # Preprocess text: remove extra spaces and normalize line breaks
    text = re.sub(r"\s+", " ", text.strip())  # Replace multiple whitespaces with a single space

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
    chunk_counter = 1  # Initialize the chunk counter for unique chunk IDs
    sections[current_section] = {"chunk_number": chunk_counter, "content": ""}

    # Use spaCy to split the text into sentences
    doc = nlp(text)

    for sent in doc.sents:
        line = sent.text.strip()
        line_lower = line.lower()

        # Check if the line matches any section keywords
        matched_section = detect_section(line, section_keywords, nlp)

        if matched_section:
            # Start a new section with a unique chunk number
            chunk_counter += 1
            current_section = matched_section
            sections[current_section] = {"chunk_number": chunk_counter, "content": ""}
        
        # Append the line to the current section
        sections[current_section]["content"] += " " + line

    # Remove extra spaces in sections and store the content
    for section in sections:
        sections[section]["content"] = sections[section]["content"].strip()

    return sections

def upload_to_pinecone(sections, file_name):
    """Upload the CV chunks to Pinecone."""
    upserts = []
    
    for section_name, section_data in sections.items():
        chunk_number = section_data["chunk_number"]
        content = section_data["content"]
        
        # Generate embedding for the chunk
        embedding = embedding_model.encode(content)
        
        # Create metadata to store along with the vector
        metadata = {
            "file_name": file_name,
            "section": section_name,
            "chunk_number": chunk_number,
            "content": content
        }
        
        # Prepare the upsert data (ID, vector, metadata)
        upserts.append({
            "id": f"{file_name}-{section_name}-{chunk_number}",
            "values": embedding.tolist(),  # Convert numpy array to list
            "metadata": metadata
        })

    # Upload the chunks to Pinecone
    index.upsert(vectors=upserts)

def process_multiple_cvs(folder_path):
    """Process all PDFs in a folder, chunk them into sections, and upload to Pinecone."""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}")
            try:
                sections = chunk_cv_with_spacy(file_path)
                upload_to_pinecone(sections, filename)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("All CV chunks uploaded to Pinecone.")

# Example usage
folder_path = r"E:\INTERN-BISTEC\CV_Chatbot\CV Store Local"  # Folder containing CVs

process_multiple_cvs(folder_path)
