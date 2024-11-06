import os
import shutil
import pdfplumber
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
    load_index_from_storage,
)
import re


load_dotenv()
OpenAI_Key = os.getenv("Open_ai_key")
os.environ["OPENAI_API_KEY"] = OpenAI_Key

PERSIST_DIR = "./storage"
index = None
owner_names = []  


SKILL_KEYWORDS = ["Python", "Django", "AWS", "JavaScript", "React", "Machine Learning"]

def clear_storage():
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
        print("Cleared existing index storage.")

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    print(f"Warning: No text found on page {page_num + 1} of {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return text

def extract_skills(content):
    """Identify and return skills found in the content based on skill keywords."""
    found_skills = []
    for skill in SKILL_KEYWORDS:
        if re.search(r'\b' + re.escape(skill) + r'\b', content, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills

def rebuild_index():
    global index, owner_names
    owner_names = []  

    clear_storage()
    cv_files = os.listdir("data")[:5]

    if not cv_files:
        print("Data directory is empty. Index will not be created.")
        return

    documents = []
    for file in cv_files:
        file_path = os.path.join("data", file)
        if os.path.isfile(file_path):
            print(f"Loading CV from: {file_path}")
            if file.lower().endswith(".pdf"):
                content = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

            owner_name = os.path.splitext(file)[0]
            owner_names.append(owner_name)
            print(f"Extracted content for {owner_name}: {len(content)} characters.")

            if content.strip():
               
                skills = extract_skills(content)
                document = Document(content=content, metadata={"owner_name": owner_name, "skills": skills})
                documents.append(document)
                print(f"Document created for {owner_name} with skills: {skills}")
            else:
                print(f"Skipped empty document: {file_path}")

    print(f"Loaded {len(documents)} documents for indexing.")

    if documents:
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("Index has been created and stored.")
    else:
        print("No valid documents found to index.")

def query_cv(prompt):
    global index

    if index is None:
        raise ValueError("Index has not been initialized. Please check the data directory or persisted storage.")

    
    required_skills = extract_skills(prompt)
    print(f"Searching for candidates with skills: {required_skills}")

    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)

    if not response or str(response).strip() == "":
        print("Received an empty response from the query engine.")
        return "No relevant information found in the documents."

    response_text = str(response)
    print("Query response:", response_text)

    # Retrieve documents from the storage context
    storage_context = StorageContext(persist_dir=PERSIST_DIR)
    indexed_documents = storage_context.documents  # Retrieve all stored documents
    
    # Rank candidates by matching score
    candidates_scores = []
    for doc_id, document in indexed_documents.items():
        doc_skills = document.metadata.get("skills", [])
        matching_score = sum(skill in doc_skills for skill in required_skills)  # Count matching skills
        if matching_score > 0:  # Only consider candidates with at least one matching skill
            candidates_scores.append((document.metadata["owner_name"], matching_score))

    # Sort candidates by score in descending order
    ranked_candidates = sorted(candidates_scores, key=lambda x: x[1], reverse=True)

    # Format results
    if ranked_candidates:
        ranked_list = "\n".join([f"{name}: {score} matching skills" for name, score in ranked_candidates])
        return f"Ranked candidates by matching skills:\n{ranked_list}"
    else:
        return "No relevant information found in the documents."


rebuild_index()


result = query_cv("I have a job description that requires Python and Django skills. Who among these candidates has these skills?")
print(result)

print(query_cv("List all skills of each candidate."))
print(query_cv("Who has experience with Python?"))
print(query_cv("Who has managed projects in AWS?"))
